let currentAnalysisId = null;
let statusInterval = null;
let currentAnalysisType = null;

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const urlInput = document.getElementById('urlInput');
const analyzeUrlBtn = document.getElementById('analyzeUrlBtn');

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    .success { color: #48bb78; font-weight: bold; }
    .error { color: #f56565; font-weight: bold; }
    .warning { color: #ed8936; font-weight: bold; }
    .critical { color: #c53030; font-weight: bold; }
`;
document.head.appendChild(style);

// Check for analysis ID in URL
(function() {
    const urlParams = new URLSearchParams(window.location.search);
    const analysisId = urlParams.get('analysis');
    
    if (analysisId) {
        console.log('Analysis ID found in URL:', analysisId);
        setTimeout(() => {
            document.querySelector('.url-section').style.display = 'none';
            document.querySelector('.upload-section').style.display = 'none';
            document.getElementById('analysisProgress').style.display = 'block';
            document.getElementById('analysisId').textContent = `Analysis ID: ${analysisId.substring(0,8)}...`;
            currentAnalysisId = analysisId;
            startStatusPolling(analysisId);
        }, 500);
    }
})();

// File upload handlers
uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length) {
        handleFile(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        handleFile(e.target.files[0]);
    }
});

// URL Analysis
analyzeUrlBtn.addEventListener('click', () => {
    const url = urlInput.value.trim();
    if (url) {
        analyzeUrl(url);
    } else {
        alert('Please enter a URL');
    }
});

urlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        const url = urlInput.value.trim();
        if (url) {
            analyzeUrl(url);
        }
    }
});

async function analyzeUrl(url) {
    try {
        new URL(url);
    } catch {
        alert('Please enter a valid URL');
        return;
    }

    document.querySelector('.url-section').style.display = 'none';
    document.querySelector('.upload-section').style.display = 'none';
    document.getElementById('analysisProgress').style.display = 'block';
    document.getElementById('progressStatus').textContent = 'Sending URL for analysis...';
    
    try {
        const response = await fetch('/api/analyze-url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        
        if (data.error) throw new Error(data.error);

        if (data.decision === 'allow') {
            alert('This file type is not monitored. Opening in new tab...');
            window.open(url, '_blank');
            resetInterface();
            return;
        }

        currentAnalysisId = data.analysis_id;
        currentAnalysisType = 'url';
        document.getElementById('analysisId').textContent = `Analysis ID: ${currentAnalysisId.substring(0,8)}...`;
        startStatusPolling(currentAnalysisId);
        
    } catch (error) {
        console.error('URL analysis error:', error);
        alert('Error analyzing URL: ' + error.message);
        resetInterface();
    }
}

async function handleFile(file) {
    if (file.size > 500 * 1024 * 1024) {
        alert('File too large. Maximum size is 500MB.');
        return;
    }

    document.querySelector('.url-section').style.display = 'none';
    document.querySelector('.upload-section').style.display = 'none';
    document.getElementById('analysisProgress').style.display = 'block';
    
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/analyze', { method: 'POST', body: formData });
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const data = await response.json();
        if (data.error) throw new Error(data.error);

        currentAnalysisId = data.analysis_id;
        currentAnalysisType = data.type;
        document.getElementById('analysisId').textContent = `Analysis ID: ${currentAnalysisId.substring(0,8)}...`;
        startStatusPolling(currentAnalysisId);
        
    } catch (error) {
        console.error('Upload error:', error);
        alert('Error uploading file: ' + error.message);
        resetInterface();
    }
}

function startStatusPolling(analysisId) {
    statusInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/status/${analysisId}`);
            if (!response.ok) throw new Error(`Status check failed: ${response.status}`);
            const data = await response.json();
            if (data.error) throw new Error(data.error);

            if (data.progress !== undefined) {
                document.getElementById('progressBar').style.width = data.progress + '%';
                let statusMsg = data.stage || '';
                if (data.type === 'zip' && data.completed_files !== undefined && data.total_files) {
                    statusMsg += ` (${data.completed_files}/${data.total_files} files)`;
                }
                document.getElementById('progressStatus').textContent = statusMsg;
            }

            if (data.status === 'completed') {
                clearInterval(statusInterval);
                showResults(analysisId);
            } else if (data.status === 'failed') {
                clearInterval(statusInterval);
                alert('Analysis failed: ' + (data.error || 'Unknown error'));
                resetInterface();
            }
            
        } catch (error) {
            console.error('Status check failed:', error);
        }
    }, 1500);
}

async function showResults(analysisId) {
    try {
        const response = await fetch(`/api/results/${analysisId}`);
        if (!response.ok) throw new Error(`Failed to load results: ${response.status}`);
        const results = await response.json();
        
        document.getElementById('analysisProgress').style.display = 'none';
        document.getElementById('resultsSection').style.display = 'block';
        
        if (results.files) {
            showBatchResults(analysisId, results);
        } else {
            showSingleFileResults(analysisId, results);
        }
        
    } catch (error) {
        console.error('Failed to load results:', error);
        alert('Error loading results: ' + error.message);
    }
}

function showSingleFileResults(analysisId, results) {
    // Update threat level
    const threatLevel = document.getElementById('threatLevel');
    const threatLevelText = results.threat_level || 'UNKNOWN';
    threatLevel.textContent = threatLevelText;
    threatLevel.className = `threat-level ${threatLevelText.toLowerCase().replace(/\s/g, '')}`;
    
    // Update risk score
    document.getElementById('riskScore').textContent = results.risk_score || 0;
    
    // Update all tabs
    document.getElementById('staticAnalysis').innerHTML = formatStaticAnalysis(results.static_analysis || {});
    document.getElementById('behavioralAnalysis').innerHTML = formatBehavioralAnalysis(results.behavioral_analysis || {});
    document.getElementById('aiAnalysis').innerHTML = formatAIAnalysis(results.ai_analysis || {});
    document.getElementById('summaryAnalysis').innerHTML = formatSummary(results);
    
    // Add download buttons
    addDownloadButtons(analysisId, results);
}

function addDownloadButtons(analysisId, results) {
    const summaryDiv = document.getElementById('summaryAnalysis');
    const filename = results.static_analysis?.filename || '';
    const scriptExtensions = ['.py', '.js', '.bat', '.ps1', '.sh', '.php', '.rb', '.pl', '.vbs'];
    const isScript = scriptExtensions.some(ext => filename.toLowerCase().endsWith(ext));
    
    let buttons = `
        <div class="sanitization-section" style="margin-top: 20px; padding: 20px; background: #f7fafc; border-radius: 10px;">
            <h4>🛡️ Download Options</h4>
            <div class="download-buttons" style="display: flex; gap: 10px; margin-top: 15px;">
                <button class="btn btn-primary" onclick="downloadOriginal('${analysisId}')" style="padding: 10px 20px; background: #4299e1; color: white; border: none; border-radius: 6px; cursor: pointer;">
                    📄 Download Original File
                </button>
    `;
    
    if (isScript && results.risk_score >= 10) {
        buttons += `
            <button class="btn btn-success" onclick="sanitizeAndDownload('${analysisId}')" style="padding: 10px 20px; background: #48bb78; color: white; border: none; border-radius: 6px; cursor: pointer;">
                🛡️ Sanitize & Download
            </button>
        `;
    }
    
    buttons += `
            </div>
            <div id="sanitizationProgress" style="display: none; margin-top: 15px;">
                <p>⏳ Sanitizing code... please wait</p>
                <div class="progress-bar-container"><div class="progress-bar" style="width: 50%"></div></div>
            </div>
            <div id="sanitizationResult" style="display: none; margin-top: 15px;"></div>
        </div>
    `;
    
    summaryDiv.innerHTML += buttons;
}

function downloadOriginal(analysisId) {
    window.open(`/api/download/${analysisId}/original?t=${Date.now()}`, '_blank');
}

async function sanitizeAndDownload(analysisId) {
    document.getElementById('sanitizationProgress').style.display = 'block';
    
    try {
        const response = await fetch(`/api/sanitize/${analysisId}`, { method: 'POST' });
        const data = await response.json();
        
        if (data.error) throw new Error(data.error);
        
        document.getElementById('sanitizationProgress').style.display = 'none';
        const resultDiv = document.getElementById('sanitizationResult');
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = `
            <div style="background: #c6f6d5; padding: 15px; border-radius: 8px;">
                <p>✅ ${data.message}</p>
                <button class="btn btn-success" onclick="window.open('/api/download/${analysisId}/sanitized?t=${Date.now()}', '_blank')" style="margin-top: 10px; padding: 8px 16px; background: #48bb78; color: white; border: none; border-radius: 6px; cursor: pointer;">
                    📥 Download Sanitized File
                </button>
            </div>
        `;
    } catch (error) {
        document.getElementById('sanitizationProgress').style.display = 'none';
        alert('Error sanitizing file: ' + error.message);
    }
}

// ===== FORMATTING FUNCTIONS =====

function formatStaticAnalysis(staticAnalysis) {
    let html = '<div class="analysis-details">';
    
    // File info
    html += '<h4>📄 File Information</h4>';
    html += `<p><strong>Filename:</strong> ${staticAnalysis.filename || 'Unknown'}</p>`;
    html += `<p><strong>Size:</strong> ${formatBytes(staticAnalysis.size || 0)}</p>`;
    html += `<p><strong>File Type:</strong> ${staticAnalysis.file_type || 'Unknown'}</p>`;
    html += `<p><strong>Entropy:</strong> ${staticAnalysis.entropy || 0} (higher = more random/packed)</p>`;
    
    // Verdict
    if (staticAnalysis.verdict) {
        const verdictClass = staticAnalysis.verdict === 'MALICIOUS' ? 'error' : 
                            staticAnalysis.verdict === 'SUSPICIOUS' ? 'warning' : 'success';
        html += `<p><strong>Verdict:</strong> <span class="${verdictClass}">${staticAnalysis.verdict}</span></p>`;
        html += `<p><strong>What this means:</strong> ${staticAnalysis.what_this_means || 'Analysis complete'}</p>`;
    }
    
    // Risk Factors
    if (staticAnalysis.risk_factors && staticAnalysis.risk_factors.length > 0) {
        html += '<h4 style="color: #e53e3e; margin-top: 20px;">⚠️ Risk Factors Detected</h4>';
        for (const factor of staticAnalysis.risk_factors) {
            html += `
                <div style="background: #fff5f5; padding: 12px; margin: 10px 0; border-radius: 8px; border-left: 3px solid #fc8181;">
                    <p><strong>${factor.type}</strong> - ${factor.details}</p>
                    <p style="font-size: 13px; color: #666; margin-top: 5px;">💡 ${factor.explanation}</p>
                </div>
            `;
        }
    }
    
    // Hashes
    html += '<details style="margin-top: 15px;"><summary style="cursor: pointer;">🔑 File Hashes (for security researchers)</summary>';
    html += `<p><strong>MD5:</strong> <code>${staticAnalysis.md5 || 'N/A'}</code></p>`;
    html += `<p><strong>SHA256:</strong> <code>${staticAnalysis.sha256 || 'N/A'}</code></p>`;
    html += '</details>';
    
    html += '</div>';
    return html;
}

function formatBehavioralAnalysis(behavioralAnalysis) {
    let html = '<div class="analysis-details">';
    
    // Summary
    if (behavioralAnalysis.what_happened) {
        html += `
            <div style="background: #e2e8f0; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <p><strong>📋 Summary:</strong> ${behavioralAnalysis.what_happened}</p>
            </div>
        `;
    }
    
    // Execution status
    if (behavioralAnalysis.execution_success) {
        html += '<p class="success">✅ File was executed in sandbox</p>';
    } else if (behavioralAnalysis.error) {
        html += `<p class="error">❌ Execution error: ${behavioralAnalysis.error}</p>`;
    }
    
    // Suspicious Activities
    if (behavioralAnalysis.suspicious_activities && behavioralAnalysis.suspicious_activities.length > 0) {
        html += '<h4 style="color: #e53e3e;">🚨 Suspicious Activities Found</h4>';
        for (const activity of behavioralAnalysis.suspicious_activities) {
            html += `
                <div style="background: #fff5f5; padding: 12px; margin: 10px 0; border-radius: 8px; border-left: 3px solid #fc8181;">
                    <strong>${activity.activity || 'Suspicious Activity'}</strong><br>
                    ${activity.explanation ? `<span style="font-size: 13px;">${activity.explanation}</span>` : ''}
                    ${activity.path ? `<code style="font-size: 12px; display: block; margin-top: 5px;">${activity.path}</code>` : ''}
                </div>
            `;
        }
    } else {
        html += `
            <div style="background: #c6f6d5; padding: 15px; border-radius: 8px; margin-top: 15px;">
                <p>✅ <strong>No suspicious behavior detected</strong></p>
                <p style="margin-top: 10px;">The file executed normally without any malicious actions.</p>
            </div>
        `;
    }
    
    // Normal activities (collapsible)
    if (behavioralAnalysis.normal_activities && behavioralAnalysis.normal_activities.length > 0) {
        html += `
            <details style="margin-top: 15px;">
                <summary style="cursor: pointer; color: #4299e1;">📁 View normal file operations (${behavioralAnalysis.normal_activities.length})</summary>
                <ul style="margin-top: 10px;">
                    ${behavioralAnalysis.normal_activities.slice(0, 10).map(act => 
                        `<li><code>${act.path || act.activity}</code> - ${act.explanation || 'Normal operation'}</li>`
                    ).join('')}
                </ul>
            </details>
        `;
    }
    
    html += '</div>';
    return html;
}

function formatAIAnalysis(aiAnalysis) {
    let html = '<div class="analysis-details">';
    
    if (aiAnalysis.error) {
        html += `<p class="error">⚠️ AI Analysis Error: ${aiAnalysis.error}</p>`;
        html += '</div>';
        return html;
    }
    
    if (aiAnalysis.analysis_time) {
        html += `<p><small>⏱️ Analysis time: ${aiAnalysis.analysis_time.toFixed(2)}s</small></p>`;
    }
    
    // Plain language summary
    if (aiAnalysis.plain_language_summary) {
        html += `
            <div style="background: #ebf8ff; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                <h4 style="margin: 0 0 10px 0;">🤖 AI Analysis (Plain English)</h4>
                <p style="margin: 0; line-height: 1.6;">${aiAnalysis.plain_language_summary}</p>
            </div>
        `;
    }
    
    // Should you run it
    if (aiAnalysis.should_you_run_it) {
        const isSafe = aiAnalysis.should_you_run_it === 'YES';
        const isDangerous = aiAnalysis.should_you_run_it === 'NO';
        const bgColor = isSafe ? '#c6f6d5' : (isDangerous ? '#fed7d7' : '#feebc8');
        const textColor = isSafe ? '#22543d' : (isDangerous ? '#742a2a' : '#7b341e');
        
        html += `
            <div style="background: ${bgColor}; padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center;">
                <p style="margin: 0; font-size: 18px; font-weight: bold; color: ${textColor};">
                    ${isSafe ? '✅' : (isDangerous ? '🚨' : '⚠️')} 
                    ${aiAnalysis.should_you_run_it === 'YES' ? 'SAFE TO RUN' : 
                      (aiAnalysis.should_you_run_it === 'NO' ? 'DO NOT RUN!' : 'RUN WITH CAUTION')}
                </p>
            </div>
        `;
    }
    
    // Risk assessment
    if (aiAnalysis.risk_assessment) {
        html += `
            <div style="margin-bottom: 15px;">
                <strong>Risk Assessment:</strong> ${aiAnalysis.risk_assessment}
            </div>
        `;
    }
    
    html += '</div>';
    return html;
}

function formatSummary(results) {
    let html = '<div class="analysis-details">';
    
    // User-friendly verdict
    if (results.user_friendly_summary) {
        const summary = results.user_friendly_summary;
        const colors = { 'green': '#48bb78', 'yellow': '#ecc94b', 'orange': '#ed8936', 'red': '#f56565', 'darkred': '#c53030' };
        const bgColor = colors[summary.verdict_color] || '#718096';
        
        html += `
            <div style="background: ${bgColor}20; border-left: 4px solid ${bgColor}; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h2 style="margin: 0 0 10px 0; font-size: 28px;">${summary.verdict_icon} ${summary.verdict_text}</h2>
                <p style="font-size: 16px; margin-bottom: 15px;"><strong>${summary.one_line_summary}</strong></p>
                <p><strong>🔍 What happened:</strong> ${summary.what_happened}</p>
                <p><strong>📋 Recommendation:</strong> ${summary.recommendation}</p>
            </div>
        `;
        
        if (summary.risk_factors && summary.risk_factors.length > 0) {
            html += `
                <div style="margin-bottom: 20px;">
                    <h3>⚠️ Risk Factors Found</h3>
                    <ul>${summary.risk_factors.map(f => `<li>${f}</li>`).join('')}</ul>
                </div>
            `;
        }
        
        if (summary.ai_says && summary.ai_says !== 'AI analysis not available') {
            html += `
                <div style="background: #f0f0f0; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <h3>🤖 AI Analysis</h3>
                    <p>${summary.ai_says}</p>
                </div>
            `;
        }
    }
    
    // Risk score display
    const riskLevel = results.threat_level || 'UNKNOWN';
    const riskColor = getRiskColor(riskLevel);
    const riskScore = results.risk_score || 0;
    
    html += `
        <div style="text-align: center; padding: 20px;">
            <div class="score-circle" style="background: ${riskColor};">${riskScore}</div>
            <p><strong>Risk Score: ${riskScore}/100</strong></p>
            <p>${getRiskExplanation(riskScore)}</p>
        </div>
    `;
    
    html += '</div>';
    return html;
}

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

function getRiskColor(level) {
    const levelStr = (level || '').toLowerCase();
    if (levelStr.includes('safe')) return '#48bb78';
    if (levelStr.includes('low')) return '#ecc94b';
    if (levelStr.includes('medium')) return '#ed8936';
    if (levelStr.includes('high')) return '#f56565';
    if (levelStr.includes('critical')) return '#c53030';
    return '#718096';
}

function getRiskExplanation(score) {
    if (score < 20) return "✅ This file appears safe to use.";
    if (score < 40) return "⚠️ Low risk - be cautious with this file.";
    if (score < 60) return "⚠️⚠️ Medium risk - don't run on your main computer.";
    if (score < 80) return "🚨 High risk - this file is likely malicious!";
    return "🔥🔥 CRITICAL - Do NOT run this file! It will harm your system.";
}

function showTab(tabName) {
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.getElementById(tabName + 'Tab').classList.add('active');
}

function showBatchResults(analysisId, results) {
    const threatLevel = document.getElementById('threatLevel');
    const threatLevelText = results.overall?.threat_level || 'UNKNOWN';
    threatLevel.textContent = threatLevelText;
    threatLevel.className = `threat-level ${threatLevelText.toLowerCase().replace(/\s/g, '')}`;
    document.getElementById('riskScore').textContent = results.overall?.risk_score || 0;
    
    let batchHTML = '<div class="batch-summary"><h3>📦 ZIP Analysis Complete</h3>';
    batchHTML += `<p>Total files: ${results.total || 0}</p>`;
    batchHTML += `<p>Completed: ${results.completed || 0}</p>`;
    batchHTML += `<p>Failed: ${results.failed || 0}</p></div>`;
    batchHTML += '<h4>📄 Individual File Results</h4><div class="file-results-list">';
    
    for (const [fileName, fileData] of Object.entries(results.files || {})) {
        if (fileData.status === 'completed' && fileData.result) {
            const risk = fileData.result.risk_score || 0;
            const threat = fileData.result.threat_level || 'UNKNOWN';
            const riskColor = getRiskColor(threat);
            batchHTML += `
                <div class="file-result-item" style="border-left: 4px solid ${riskColor}; padding: 10px; margin: 10px 0; background: #f7fafc; border-radius: 8px;">
                    <p><strong>📄 ${fileName}</strong> - Risk: ${risk} (${threat})</p>
                    <button class="btn btn-small" onclick="showFileDetails('${analysisId}', '${fileName}')" style="padding: 5px 10px; background: #667eea; color: white; border: none; border-radius: 5px; cursor: pointer;">View Details</button>
                </div>
            `;
        }
    }
    batchHTML += '</div>';
    document.getElementById('summaryAnalysis').innerHTML = batchHTML;
    window.batchData = results;
    window.currentBatchId = analysisId;
}

function showFileDetails(batchId, fileName) {
    const batchData = window.batchData;
    if (!batchData || !batchData.files || !batchData.files[fileName]) return;
    const fileData = batchData.files[fileName];
    if (fileData.status !== 'completed' || !fileData.result) return;
    const results = fileData.result;
    
    document.getElementById('staticAnalysis').innerHTML = formatStaticAnalysis(results.static_analysis || {});
    document.getElementById('behavioralAnalysis').innerHTML = formatBehavioralAnalysis(results.behavioral_analysis || {});
    document.getElementById('aiAnalysis').innerHTML = formatAIAnalysis(results.ai_analysis || {});
    document.getElementById('summaryAnalysis').innerHTML = formatSummary(results) + `<p><button class="btn btn-small" onclick="showBatchSummary('${batchId}')">← Back to ZIP Summary</button></p>`;
    document.querySelectorAll('.tab-button')[0].click();
}

function showBatchSummary(batchId) {
    showResults(batchId);
}

async function cleanup() {
    if (!currentAnalysisId) return;
    try {
        const response = await fetch(`/api/clean/${currentAnalysisId}`, { method: 'POST' });
        const data = await response.json();
        if (data.status === 'cleaned') {
            alert('✅ Resources cleaned up successfully');
            resetInterface();
        }
    } catch (error) {
        console.error('Cleanup failed:', error);
        resetInterface();
    }
}

function resetInterface() {
    if (statusInterval) clearInterval(statusInterval);
    currentAnalysisId = null;
    currentAnalysisType = null;
    document.querySelector('.url-section').style.display = 'block';
    document.querySelector('.upload-section').style.display = 'block';
    document.getElementById('analysisProgress').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    fileInput.value = '';
    urlInput.value = '';
    document.getElementById('progressBar').style.width = '0%';
    document.getElementById('progressStatus').textContent = 'Waiting for file...';
}

// Add this function to display the change report after sanitization

function displayChangeReport(changeReport) {
    if (!changeReport) return '';
    
    let html = `
        <div style="background: #ebf8ff; padding: 20px; border-radius: 10px; margin-top: 20px;">
            <h4 style="margin-top: 0; color: #2c5282;">📋 Sanitization Report</h4>
            <p><strong>File:</strong> ${changeReport.filename || 'Unknown'}</p>
            <p><strong>Sanitized at:</strong> ${new Date(changeReport.sanitized_at).toLocaleString()}</p>
            <p><strong>Total vulnerabilities found:</strong> ${changeReport.total_vulnerabilities || 0}</p>
            <p><strong>${changeReport.summary || 'Sanitization complete'}</strong></p>
    `;
    
    if (changeReport.vulnerabilities_removed && changeReport.vulnerabilities_removed.length > 0) {
        html += `
            <details style="margin-top: 15px;">
                <summary style="cursor: pointer; font-weight: bold; color: #2c5282;">🔍 View Removed Vulnerabilities (${changeReport.vulnerabilities_removed.length})</summary>
                <div style="margin-top: 10px; max-height: 300px; overflow-y: auto;">
        `;
        
        for (const vuln of changeReport.vulnerabilities_removed) {
            let severityColor = '#ed8936';
            if (vuln.severity === 'CRITICAL') severityColor = '#c53030';
            else if (vuln.severity === 'HIGH') severityColor = '#e53e3e';
            else if (vuln.severity === 'MEDIUM') severityColor = '#ed8936';
            else severityColor = '#48bb78';
            
            html += `
                <div style="border-left: 3px solid ${severityColor}; padding: 10px; margin: 10px 0; background: #f7fafc; border-radius: 5px;">
                    <p><strong style="color: ${severityColor};">[${vuln.severity}] ${vuln.type}</strong></p>
                    <p style="font-size: 13px; margin: 5px 0;"><strong>Details:</strong> ${vuln.details}</p>
                    <p style="font-size: 13px; margin: 5px 0;"><strong>Why removed:</strong> ${vuln.explanation}</p>
                </div>
            `;
        }
        html += `</div></details>`;
    }
    
    if (changeReport.changes_made && changeReport.changes_made.length > 0) {
        html += `
            <details style="margin-top: 15px;">
                <summary style="cursor: pointer; font-weight: bold; color: #2c5282;">✏️ View Changes Made</summary>
                <div style="margin-top: 10px;">
        `;
        
        for (const change of changeReport.changes_made) {
            html += `
                <div style="background: #2d3748; color: #e2e8f0; padding: 10px; margin: 8px 0; border-radius: 5px; font-family: monospace; font-size: 12px;">
                    <div><span style="color: #fc8181;">REMOVED:</span> ${change.original}</div>
                    <div style="color: #a0aec0; margin-top: 5px;">Reason: ${change.reason}</div>
                </div>
            `;
        }
        html += `</div></details>`;
    }
    
    html += `</div>`;
    return html;
}

// Update the sanitizeAndDownload function to show the report
async function sanitizeAndDownload(analysisId) {
    document.getElementById('sanitizationProgress').style.display = 'block';
    
    try {
        const response = await fetch(`/api/sanitize/${analysisId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.error) throw new Error(data.error);
        
        document.getElementById('sanitizationProgress').style.display = 'none';
        const resultDiv = document.getElementById('sanitizationResult');
        resultDiv.style.display = 'block';
        
        // Display change report
        const changeReportHtml = data.change_report ? displayChangeReport(data.change_report) : '';
        
        resultDiv.innerHTML = `
            <div style="background: #c6f6d5; padding: 15px; border-radius: 8px;">
                <p>✅ ${data.message}</p>
                <button class="btn btn-success" onclick="window.open('/api/download/${analysisId}/sanitized?t=${Date.now()}', '_blank')" 
                    style="margin-top: 10px; padding: 8px 16px; background: #48bb78; color: white; border: none; border-radius: 6px; cursor: pointer;">
                    📥 Download Sanitized File
                </button>
            </div>
            ${changeReportHtml}
        `;
        
    } catch (error) {
        document.getElementById('sanitizationProgress').style.display = 'none';
        alert('Error sanitizing file: ' + error.message);
    }
}