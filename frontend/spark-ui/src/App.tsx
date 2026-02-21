import { FormEvent, ReactNode, useEffect, useMemo, useState } from "react";
import { apiRequest } from "./api";
import { generateDevJwt } from "./auth";

type OutputState = Record<string, string>;
type TabKey = "workflow" | "system" | "patients" | "devices" | "models" | "audit";

const VALID_TABS = new Set<TabKey>(["workflow", "system", "patients", "devices", "models", "audit"]);

function getTabFromUrl(): TabKey {
  const params = new URLSearchParams(window.location.search);
  const tab = params.get("tab");
  return tab && VALID_TABS.has(tab as TabKey) ? (tab as TabKey) : "workflow";
}

function pretty(value: unknown): string {
  return typeof value === "string" ? value : JSON.stringify(value, null, 2);
}

function parseJson(text: string): unknown {
  return text.trim() ? JSON.parse(text) : {};
}

function SparkCard(props: { title: string; children: ReactNode }) {
  return (
    <section className="spark-card">
      <h2>{props.title}</h2>
      {props.children}
    </section>
  );
}

function SparkField(props: { label: string; children: ReactNode }) {
  return (
    <div className="spark-field">
      <label>{props.label}</label>
      {props.children}
    </div>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState<TabKey>(getTabFromUrl);
  const [baseUrl, setBaseUrl] = useState(import.meta.env.VITE_API_BASE_URL || "/api");
  const [token, setToken] = useState("");
  const [jwtSubject, setJwtSubject] = useState("dev-admin");
  const [jwtRoles, setJwtRoles] = useState("admin,clinician,auditor");
  const [jwtSecret, setJwtSecret] = useState("dev-insecure-jwt-secret");

  const [health, setHealth] = useState("unknown");
  const [busy, setBusy] = useState<Record<string, boolean>>({});
  const [output, setOutput] = useState<OutputState>({});

  const [patientCreate, setPatientCreate] = useState({ mrn: "MRN-001", demographics: '{"age": 64, "sex": "F"}' });
  const [patientId, setPatientId] = useState("1");

  const [deviceCreate, setDeviceCreate] = useState({
    device_id: "pump-00",
    firmware_version: "0.1.0",
    gateway_version: "0.1.0",
    config_payload: '{"ward":"ICU-1"}'
  });
  const [deviceConfigId, setDeviceConfigId] = useState("1");

  const [sessionCreate, setSessionCreate] = useState({ patient_id: "1", device_configuration_id: "1", clinician_target_map_mmhg: "65" });
  const [sessionId, setSessionId] = useState("1");
  const [selectedDrug, setSelectedDrug] = useState<{ id: number; name: string } | null>(null);

  const [drugCreate, setDrugCreate] = useState({
    drug_name: "Norepinephrine",
    concentration_mcg_per_ml: "16",
    min_rate_mcg_per_kg_min: "0.02",
    max_rate_mcg_per_kg_min: "3.3",
    max_delta_mcg_per_kg_min: "0.2",
    safety_notes: "Unit test/demo profile"
  });
  const [drugId, setDrugId] = useState("1");

  const [modelCreate, setModelCreate] = useState({
    registry_id: "map-predictor",
    version: "v0.1.0",
    dataset_hash: "abc123",
    validation_report_path: "validation/reports/dev.json",
    acceptance_summary: '{"auroc":0.91,"status":"pass"}'
  });
  const [modelId, setModelId] = useState("1");

  const [auditLimit, setAuditLimit] = useState("50");

  const roleList = useMemo(
    () => jwtRoles.split(",").map((r) => r.trim()).filter(Boolean),
    [jwtRoles]
  );

  const tabs: Array<{ key: TabKey; label: string }> = [
    { key: "workflow", label: "Session + Drug" },
    { key: "system", label: "System" },
    { key: "patients", label: "Patients" },
    { key: "devices", label: "Devices" },
    { key: "models", label: "ML Models" },
    { key: "audit", label: "Audit" }
  ];

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("tab") !== activeTab) {
      params.set("tab", activeTab);
      const nextUrl = `${window.location.pathname}?${params.toString()}${window.location.hash}`;
      window.history.replaceState(null, "", nextUrl);
    }
  }, [activeTab]);

  useEffect(() => {
    const onPopState = () => {
      setActiveTab(getTabFromUrl());
    };
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  async function run<T>(key: string, call: () => Promise<T>) {
    setBusy((b) => ({ ...b, [key]: true }));
    try {
      const result = await call();
      setOutput((o) => ({ ...o, [key]: pretty(result) }));
    } catch (error) {
      setOutput((o) => ({ ...o, [key]: `Error: ${error instanceof Error ? error.message : "Unknown error"}` }));
    } finally {
      setBusy((b) => ({ ...b, [key]: false }));
    }
  }

  async function req<T>(path: string, method: "GET" | "POST", body?: unknown): Promise<T> {
    let effectiveToken = token;
    if (!effectiveToken) {
      effectiveToken = await generateDevJwt({
        subject: jwtSubject,
        roles: roleList,
        secret: jwtSecret,
        ttlMinutes: 60
      });
      setToken(effectiveToken);
    }

    const res = await apiRequest<T>({ baseUrl, path, method, token: effectiveToken, body });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status ?? "?"}: ${res.error}`);
    }
    return res.data;
  }

  async function handleGenerateToken(e: FormEvent) {
    e.preventDefault();
    await run("auth", async () => {
      const jwt = await generateDevJwt({
        subject: jwtSubject,
        roles: roleList,
        secret: jwtSecret,
        ttlMinutes: 60
      });
      setToken(jwt);
      return { tokenGenerated: true, subject: jwtSubject, roles: roleList };
    });
  }

  async function createDrugEntry() {
    const created = await req<{ id: number; drug_name: string }>("/drug-library/", "POST", {
      drug_name: drugCreate.drug_name,
      concentration_mcg_per_ml: Number(drugCreate.concentration_mcg_per_ml),
      min_rate_mcg_per_kg_min: Number(drugCreate.min_rate_mcg_per_kg_min),
      max_rate_mcg_per_kg_min: Number(drugCreate.max_rate_mcg_per_kg_min),
      max_delta_mcg_per_kg_min: Number(drugCreate.max_delta_mcg_per_kg_min),
      safety_notes: drugCreate.safety_notes || null
    });
    const selected = { id: created.id, name: created.drug_name };
    setSelectedDrug(selected);
    setDrugId(String(created.id));
    return { selected_infusion_drug: selected, created_entry: created };
  }

  async function fetchDrugEntry() {
    const entry = await req<{ id: number; drug_name: string }>(`/drug-library/${drugId}`, "GET");
    setSelectedDrug({ id: entry.id, name: entry.drug_name });
    return { selected_infusion_drug: { id: entry.id, name: entry.drug_name }, fetched_entry: entry };
  }

  return (
    <main className="app-shell">
      <div className="spark-page">
        <header className="spark-header">
          <h1>Infusion Platform Console (React)</h1>
          <p>Tabbed console with a consolidated pump session + infusion drug workflow.</p>
        </header>

        <nav className="spark-tabs" aria-label="Application Navigation">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              type="button"
              className={`spark-tab ${activeTab === tab.key ? "active" : ""}`}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        <div className="spark-grid">
          {activeTab === "workflow" && (
            <>
              <SparkCard title="Chosen Infusion Drug">
                <form
                  className="spark-form"
                  onSubmit={(e) => {
                    e.preventDefault();
                    run("drugs", createDrugEntry);
                  }}
                >
                  <SparkField label="Drug Name">
                    <input value={drugCreate.drug_name} onChange={(e) => setDrugCreate((v) => ({ ...v, drug_name: e.target.value }))} />
                  </SparkField>
                  <div className="spark-row">
                    <SparkField label="Concentration (mcg/ml)">
                      <input
                        value={drugCreate.concentration_mcg_per_ml}
                        onChange={(e) => setDrugCreate((v) => ({ ...v, concentration_mcg_per_ml: e.target.value }))}
                      />
                    </SparkField>
                    <SparkField label="Min Rate">
                      <input
                        value={drugCreate.min_rate_mcg_per_kg_min}
                        onChange={(e) => setDrugCreate((v) => ({ ...v, min_rate_mcg_per_kg_min: e.target.value }))}
                      />
                    </SparkField>
                  </div>
                  <div className="spark-row">
                    <SparkField label="Max Rate">
                      <input
                        value={drugCreate.max_rate_mcg_per_kg_min}
                        onChange={(e) => setDrugCreate((v) => ({ ...v, max_rate_mcg_per_kg_min: e.target.value }))}
                      />
                    </SparkField>
                    <SparkField label="Max Delta">
                      <input
                        value={drugCreate.max_delta_mcg_per_kg_min}
                        onChange={(e) => setDrugCreate((v) => ({ ...v, max_delta_mcg_per_kg_min: e.target.value }))}
                      />
                    </SparkField>
                  </div>
                  <SparkField label="Safety Notes">
                    <textarea value={drugCreate.safety_notes} onChange={(e) => setDrugCreate((v) => ({ ...v, safety_notes: e.target.value }))} />
                  </SparkField>
                  <div className="spark-row">
                    <SparkField label="Entry ID (fetch/select)">
                      <input value={drugId} onChange={(e) => setDrugId(e.target.value)} />
                    </SparkField>
                    <div className="spark-actions" style={{ alignItems: "end" }}>
                      <button className="spark-button" disabled={!!busy.drugs} type="submit">Create + Select</button>
                      <button
                        className="spark-button secondary"
                        disabled={!!busy.drugs}
                        type="button"
                        onClick={() => run("drugs", fetchDrugEntry)}
                      >
                        Fetch + Select
                      </button>
                    </div>
                  </div>
                  <div className="spark-inline-note">
                    Selected drug:{" "}
                    <span className={`spark-pill ${selectedDrug ? "ok" : "warn"}`}>
                      {selectedDrug ? `${selectedDrug.name} (id:${selectedDrug.id})` : "None"}
                    </span>
                  </div>
                </form>
                {output.drugs && <pre className="spark-output">{output.drugs}</pre>}
              </SparkCard>

              <SparkCard title="Pump Session Management">
                <form
                  className="spark-form"
                  onSubmit={(e) => {
                    e.preventDefault();
                    run("sessions", async () => {
                      const session = await req("/sessions/", "POST", {
                        patient_id: Number(sessionCreate.patient_id),
                        device_configuration_id: Number(sessionCreate.device_configuration_id),
                        clinician_target_map_mmhg: Number(sessionCreate.clinician_target_map_mmhg)
                      });
                      return {
                        session,
                        chosen_infusion_drug: selectedDrug ?? "No drug selected"
                      };
                    });
                  }}
                >
                  <div className="spark-row">
                    <SparkField label="Patient ID">
                      <input value={sessionCreate.patient_id} onChange={(e) => setSessionCreate((v) => ({ ...v, patient_id: e.target.value }))} />
                    </SparkField>
                    <SparkField label="Device Configuration ID">
                      <input
                        value={sessionCreate.device_configuration_id}
                        onChange={(e) => setSessionCreate((v) => ({ ...v, device_configuration_id: e.target.value }))}
                      />
                    </SparkField>
                  </div>
                  <SparkField label="Target MAP (mmHg)">
                    <input
                      value={sessionCreate.clinician_target_map_mmhg}
                      onChange={(e) => setSessionCreate((v) => ({ ...v, clinician_target_map_mmhg: e.target.value }))}
                    />
                  </SparkField>
                  <div className="spark-row">
                    <SparkField label="Session ID (close)">
                      <input value={sessionId} onChange={(e) => setSessionId(e.target.value)} />
                    </SparkField>
                    <div className="spark-actions" style={{ alignItems: "end" }}>
                      <button className="spark-button" disabled={!!busy.sessions} type="submit">Start Session</button>
                      <button
                        className="spark-button secondary"
                        disabled={!!busy.sessions}
                        type="button"
                        onClick={() => run("sessions", () => req(`/sessions/${sessionId}/close`, "POST"))}
                      >
                        Close Session
                      </button>
                    </div>
                  </div>
                </form>
                {output.sessions && <pre className="spark-output">{output.sessions}</pre>}
              </SparkCard>
            </>
          )}

          {activeTab === "system" && (
            <SparkCard title="Connection & Auth">
              <form className="spark-form" onSubmit={handleGenerateToken}>
                <SparkField label="API Base URL">
                  <input value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} />
                </SparkField>

                <div className="spark-row">
                  <SparkField label="JWT Subject">
                    <input value={jwtSubject} onChange={(e) => setJwtSubject(e.target.value)} />
                  </SparkField>
                  <SparkField label="JWT Roles (comma-separated)">
                    <input value={jwtRoles} onChange={(e) => setJwtRoles(e.target.value)} />
                  </SparkField>
                </div>

                <SparkField label="JWT Secret (dev compose default)">
                  <input value={jwtSecret} onChange={(e) => setJwtSecret(e.target.value)} />
                </SparkField>

                <SparkField label="Bearer Token">
                  <textarea value={token} onChange={(e) => setToken(e.target.value)} />
                </SparkField>

                <div className="spark-actions">
                  <button className="spark-button" disabled={!!busy.auth} type="submit">Generate Dev JWT</button>
                  <button
                    className="spark-button secondary"
                    type="button"
                    disabled={!!busy.health}
                    onClick={() =>
                      run("health", async () => {
                        const res = await apiRequest<{ status: string }>({ baseUrl, path: "/health", method: "GET", token: "" });
                        if (!res.ok) {
                          setHealth("down");
                          throw new Error(res.error);
                        }
                        setHealth(res.data.status);
                        return res.data;
                      })
                    }
                  >
                    Check Health
                  </button>
                </div>
                <div className="spark-inline-note">
                  Health: <span className={`spark-pill ${health === "ok" ? "ok" : "warn"}`}>{health}</span>
                </div>
                {output.auth && <pre className="spark-output">{output.auth}</pre>}
                {output.health && <pre className="spark-output">{output.health}</pre>}
              </form>
            </SparkCard>
          )}

          {activeTab === "patients" && (
            <SparkCard title="Patients">
              <form
                className="spark-form"
                onSubmit={(e) => {
                  e.preventDefault();
                  run("patients", () =>
                    req("/patients/", "POST", {
                      mrn: patientCreate.mrn,
                      demographics: parseJson(patientCreate.demographics)
                    })
                  );
                }}
              >
                <SparkField label="MRN">
                  <input value={patientCreate.mrn} onChange={(e) => setPatientCreate((v) => ({ ...v, mrn: e.target.value }))} />
                </SparkField>
                <SparkField label="Demographics JSON">
                  <textarea
                    value={patientCreate.demographics}
                    onChange={(e) => setPatientCreate((v) => ({ ...v, demographics: e.target.value }))}
                  />
                </SparkField>
                <div className="spark-row">
                  <SparkField label="Patient ID (fetch)">
                    <input value={patientId} onChange={(e) => setPatientId(e.target.value)} />
                  </SparkField>
                  <div className="spark-actions" style={{ alignItems: "end" }}>
                    <button className="spark-button" disabled={!!busy.patients} type="submit">Create</button>
                    <button
                      className="spark-button secondary"
                      disabled={!!busy.patients}
                      type="button"
                      onClick={() => run("patients", () => req(`/patients/${patientId}`, "GET"))}
                    >
                      Fetch
                    </button>
                  </div>
                </div>
              </form>
              {output.patients && <pre className="spark-output">{output.patients}</pre>}
            </SparkCard>
          )}

          {activeTab === "devices" && (
            <SparkCard title="Device Configurations">
              <form
                className="spark-form"
                onSubmit={(e) => {
                  e.preventDefault();
                  run("devices", () =>
                    req("/devices/configurations", "POST", {
                      device_id: deviceCreate.device_id,
                      firmware_version: deviceCreate.firmware_version,
                      gateway_version: deviceCreate.gateway_version,
                      config_payload: parseJson(deviceCreate.config_payload)
                    })
                  );
                }}
              >
                <div className="spark-row">
                  <SparkField label="Device ID">
                    <input value={deviceCreate.device_id} onChange={(e) => setDeviceCreate((v) => ({ ...v, device_id: e.target.value }))} />
                  </SparkField>
                  <SparkField label="Firmware Version">
                    <input
                      value={deviceCreate.firmware_version}
                      onChange={(e) => setDeviceCreate((v) => ({ ...v, firmware_version: e.target.value }))}
                    />
                  </SparkField>
                </div>
                <SparkField label="Gateway Version">
                  <input value={deviceCreate.gateway_version} onChange={(e) => setDeviceCreate((v) => ({ ...v, gateway_version: e.target.value }))} />
                </SparkField>
                <SparkField label="Config Payload JSON">
                  <textarea
                    value={deviceCreate.config_payload}
                    onChange={(e) => setDeviceCreate((v) => ({ ...v, config_payload: e.target.value }))}
                  />
                </SparkField>
                <div className="spark-row">
                  <SparkField label="Configuration ID (fetch)">
                    <input value={deviceConfigId} onChange={(e) => setDeviceConfigId(e.target.value)} />
                  </SparkField>
                  <div className="spark-actions" style={{ alignItems: "end" }}>
                    <button className="spark-button" disabled={!!busy.devices} type="submit">Create</button>
                    <button
                      className="spark-button secondary"
                      disabled={!!busy.devices}
                      type="button"
                      onClick={() => run("devices", () => req(`/devices/configurations/${deviceConfigId}`, "GET"))}
                    >
                      Fetch
                    </button>
                  </div>
                </div>
              </form>
              {output.devices && <pre className="spark-output">{output.devices}</pre>}
            </SparkCard>
          )}

          {activeTab === "models" && (
            <SparkCard title="ML Models">
              <form
                className="spark-form"
                onSubmit={(e) => {
                  e.preventDefault();
                  run("models", async () => {
                    const created = await req<{ id: number }>("/ml-models/", "POST", {
                      registry_id: modelCreate.registry_id,
                      version: modelCreate.version,
                      dataset_hash: modelCreate.dataset_hash,
                      validation_report_path: modelCreate.validation_report_path,
                      acceptance_summary: parseJson(modelCreate.acceptance_summary)
                    });
                    setModelId(String(created.id));
                    return created;
                  });
                }}
              >
                <div className="spark-row">
                  <SparkField label="Registry ID">
                    <input value={modelCreate.registry_id} onChange={(e) => setModelCreate((v) => ({ ...v, registry_id: e.target.value }))} />
                  </SparkField>
                  <SparkField label="Version">
                    <input value={modelCreate.version} onChange={(e) => setModelCreate((v) => ({ ...v, version: e.target.value }))} />
                  </SparkField>
                </div>
                <SparkField label="Dataset Hash">
                  <input value={modelCreate.dataset_hash} onChange={(e) => setModelCreate((v) => ({ ...v, dataset_hash: e.target.value }))} />
                </SparkField>
                <SparkField label="Validation Report Path">
                  <input
                    value={modelCreate.validation_report_path}
                    onChange={(e) => setModelCreate((v) => ({ ...v, validation_report_path: e.target.value }))}
                  />
                </SparkField>
                <SparkField label="Acceptance Summary JSON">
                  <textarea
                    value={modelCreate.acceptance_summary}
                    onChange={(e) => setModelCreate((v) => ({ ...v, acceptance_summary: e.target.value }))}
                  />
                </SparkField>
                <div className="spark-row">
                  <SparkField label="Model ID (fetch)">
                    <input value={modelId} onChange={(e) => setModelId(e.target.value)} />
                  </SparkField>
                  <div className="spark-actions" style={{ alignItems: "end" }}>
                    <button className="spark-button" disabled={!!busy.models} type="submit">Register</button>
                    <button
                      className="spark-button secondary"
                      disabled={!!busy.models}
                      type="button"
                      onClick={() => run("models", () => req(`/ml-models/${modelId}`, "GET"))}
                    >
                      Fetch
                    </button>
                  </div>
                </div>
              </form>
              {output.models && <pre className="spark-output">{output.models}</pre>}
            </SparkCard>
          )}

          {activeTab === "audit" && (
            <SparkCard title="Audit Events">
              <form
                className="spark-form"
                onSubmit={(e) => {
                  e.preventDefault();
                  run("audit", () => req(`/audit/events?limit=${Number(auditLimit) || 50}`, "GET"));
                }}
              >
                <SparkField label="Limit">
                  <input value={auditLimit} onChange={(e) => setAuditLimit(e.target.value)} />
                </SparkField>
                <div className="spark-actions">
                  <button className="spark-button" disabled={!!busy.audit} type="submit">Load Events</button>
                </div>
              </form>
              {output.audit && <pre className="spark-output">{output.audit}</pre>}
            </SparkCard>
          )}
        </div>
      </div>
    </main>
  );
}
