const API = "http://127.0.0.1:8000";

function format(x) {
    return (x !== undefined && x !== null && !isNaN(x))
        ? Number(x).toFixed(1)
        : "--";
}

function updateStats(patients) {
    const total = patients.length;
    const high = patients.filter(p => p.risk_level === "HIGH").length;
    const medium = patients.filter(p => p.risk_level === "MEDIUM").length;
    const low = patients.filter(p => p.risk_level === "LOW").length;
    
    document.getElementById("totalPatients").textContent = total;
    document.getElementById("highRisk").textContent = high;
    document.getElementById("mediumRisk").textContent = medium;
    document.getElementById("lowRisk").textContent = low;
}

async function loadPatients() {
    try {
        const res = await fetch(API + "/patients");
        if (!res.ok) throw new Error("API not reachable");
        
        const data = await res.json();
        const patients = data.patients || [];
        const grid = document.getElementById("patientGrid");
        
        updateStats(patients);
        
        if (patients.length === 0) {
            grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:40px;opacity:0.5;">No patients found</div>';
            return;
        }
        
        grid.innerHTML = patients.map(p => {
            const riskClass = p.current_risk > 0.7 ? "risk-high" : 
                              p.current_risk > 0.4 ? "risk-medium" : "risk-low";
            
            return `
            <div class="patient-card ${riskClass}" onclick="showPatient('${p.patient_id}')">
                <div class="card-header">
                    <h3>${p.patient_id}</h3>
                    <span class="badge ${riskClass}">${p.risk_level}</span>
                </div>
                
                <div class="risk-bar-container">
                    <div class="risk-bar" style="width:${(p.current_risk * 100).toFixed(0)}%"></div>
                </div>
                <div class="risk-text">Risk: ${(p.current_risk * 100).toFixed(1)}%</div>
                
                <div class="vitals-grid">
                    <div class="vital-item">
                        <div class="v-label">❤️ HR</div>
                        <div class="v-value">${format(p.key_vitals?.hr)} <span class="unit">bpm</span></div>
                    </div>
                    <div class="vital-item">
                        <div class="v-label">🫁 SpO₂</div>
                        <div class="v-value">${format(p.key_vitals?.spo2)} <span class="unit">%</span></div>
                    </div>
                    <div class="vital-item">
                        <div class="v-label">🫁 RR</div>
                        <div class="v-value">${format(p.key_vitals?.rr)} <span class="unit">/min</span></div>
                    </div>
                    <div class="vital-item">
                        <div class="v-label">💉 SBP</div>
                        <div class="v-value">${format(p.key_vitals?.sbp)} <span class="unit">mmHg</span></div>
                    </div>
                </div>
            </div>`;
        }).join("");
        
    } catch (e) {
        document.getElementById("patientGrid").innerHTML = 
            '<div style="grid-column:1/-1;text-align:center;padding:40px;">⚠️ API not reachable</div>';
        console.error(e);
    }
}

async function showPatient(id) {
    const modal = document.getElementById("modal");
    modal.classList.add("active");
    document.getElementById("modalTitle").innerText = id;
    document.getElementById("modalBody").innerHTML = '<div class="loading-spinner">Loading...</div>';
    
    try {
        const res = await fetch(API + "/patient/" + id);
        if (!res.ok) throw new Error("Failed to fetch");
        const data = await res.json();
        const v = data.vitals || {};
        const explanation = data.shap_explanation || [];
        
        document.getElementById("modalBody").innerHTML = `
            <div class="modal-risk-header ${data.risk_level?.toLowerCase()}">
                Risk: ${(data.current_risk * 100).toFixed(1)}% — ${data.risk_level}
            </div>
            
            <div class="recommendation-box ${data.risk_level?.toLowerCase()}">
                ${data.recommendation}
            </div>
            
            <h3>📊 Vitals</h3>
            <div class="modal-vitals">
                <div><span>❤️ HR:</span> ${format(v.heart_rate)} bpm</div>
                <div><span>🫁 SpO₂:</span> ${format(v.spo2)}%</div>
                <div><span>🫁 RR:</span> ${format(v.respiratory_rate)} /min</div>
                <div><span>💉 BP:</span> ${v.blood_pressure || "--"} mmHg</div>
            </div>
            
            <h3>🔍 Top Risk Factors (SHAP)</h3>
            <div class="shap-list">
                ${explanation.length > 0 ? explanation.map(e => `
                    <div class="shap-item">
                        <span class="feature-name">${e.feature}</span>
                        <span class="impact ${e.direction}">
                            ${e.impact > 0 ? '↑' : '↓'} ${Math.abs(e.impact).toFixed(3)}
                        </span>
                        <span class="direction-text">${e.direction}s risk</span>
                    </div>
                `).join("") : '<div class="shap-item">No explanation available</div>'}
            </div>
        `;
    } catch (e) {
        document.getElementById("modalBody").innerHTML = "Error loading patient data";
        console.error(e);
    }
}

function closeModal() {
    document.getElementById("modal").classList.remove("active");
}

setInterval(loadPatients, 15000);
loadPatients();