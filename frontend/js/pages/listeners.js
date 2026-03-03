/* Listeners management page — FTP server, Email/IMAP, Webhook */
const ListenersPage = {
    async render() {
        const content = document.getElementById('app-content');
        content.innerHTML = '<div class="loading-spinner">Loading listeners...</div>';

        try {
            const [status, settings] = await Promise.all([
                API.getJSON('/api/listeners/status'),
                API.getJSON('/api/listeners/settings'),
            ]);

            content.innerHTML = `
                <h2 style="margin-bottom: 16px;">Listeners & Integrations</h2>

                <div class="stats-grid" style="margin-bottom: 24px;">
                    <div class="stat-card">
                        <div class="stat-value">${status.ftp.running ? 'Active' : 'Stopped'}</div>
                        <div class="stat-label">FTP Server</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${status.email.running ? 'Active' : 'Stopped'}</div>
                        <div class="stat-label">Email Listener</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">Ready</div>
                        <div class="stat-label">Webhook Endpoint</div>
                    </div>
                </div>

                <!-- FTP Server -->
                <div class="card" style="margin-bottom: 24px;">
                    <div class="card-header">
                        <span class="card-title">FTP Server</span>
                        <div class="btn-group">
                            <button class="btn btn-sm ${status.ftp.running ? 'btn-danger' : 'btn-primary'}" id="ftp-toggle-btn">
                                ${status.ftp.running ? 'Stop' : 'Start'}
                            </button>
                        </div>
                    </div>
                    <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 12px;">
                        Embedded FTP server for receiving EDI files. External systems can upload files which are auto-parsed on receipt.
                    </p>
                    ${status.ftp.running ? `<p style="font-size: 0.85rem;"><span class="badge badge-success">Running</span> on port <strong>${status.ftp.port}</strong> &mdash; directory: <code>${status.ftp.directory}</code></p>` : ''}
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 12px;">
                        <div>
                            <label style="font-size: 0.8rem; color: var(--text-secondary);">Port</label>
                            <input type="number" id="ftp-port" value="${settings.sftp_port || '2121'}" style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: var(--radius-sm); background: var(--bg-secondary); color: var(--text-primary);">
                        </div>
                        <div>
                            <label style="font-size: 0.8rem; color: var(--text-secondary);">Directory (optional)</label>
                            <input type="text" id="ftp-directory" value="${settings.sftp_directory || ''}" placeholder="~/RemitView/ftp_incoming" style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: var(--radius-sm); background: var(--bg-secondary); color: var(--text-primary);">
                        </div>
                        <div>
                            <label style="font-size: 0.8rem; color: var(--text-secondary);">Username</label>
                            <input type="text" id="ftp-username" value="${settings.sftp_username || 'remitview'}" style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: var(--radius-sm); background: var(--bg-secondary); color: var(--text-primary);">
                        </div>
                        <div>
                            <label style="font-size: 0.8rem; color: var(--text-secondary);">Password</label>
                            <input type="password" id="ftp-password" value="${settings.sftp_password || 'remitview'}" style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: var(--radius-sm); background: var(--bg-secondary); color: var(--text-primary);">
                        </div>
                    </div>
                    <button class="btn btn-outline btn-sm" id="save-ftp-btn" style="margin-top: 12px;">Save FTP Settings</button>
                </div>

                <!-- Email/IMAP Listener -->
                <div class="card" style="margin-bottom: 24px;">
                    <div class="card-header">
                        <span class="card-title">Email / IMAP Listener</span>
                        <div class="btn-group">
                            <button class="btn btn-sm btn-outline" id="email-check-btn">Check Now</button>
                            <button class="btn btn-sm ${status.email.running ? 'btn-danger' : 'btn-primary'}" id="email-toggle-btn">
                                ${status.email.running ? 'Stop' : 'Start'}
                            </button>
                        </div>
                    </div>
                    <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 12px;">
                        Polls an IMAP inbox for emails with EDI/PDF attachments and auto-imports them.
                    </p>
                    ${status.email.running ? `<p style="font-size: 0.85rem;"><span class="badge badge-success">Running</span> polling <strong>${status.email.host}</strong> as ${status.email.username}</p>` : ''}
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 12px;">
                        <div>
                            <label style="font-size: 0.8rem; color: var(--text-secondary);">IMAP Host</label>
                            <input type="text" id="email-host" value="${settings.email_imap_host || ''}" placeholder="imap.gmail.com" style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: var(--radius-sm); background: var(--bg-secondary); color: var(--text-primary);">
                        </div>
                        <div>
                            <label style="font-size: 0.8rem; color: var(--text-secondary);">IMAP Port</label>
                            <input type="number" id="email-port" value="${settings.email_imap_port || '993'}" style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: var(--radius-sm); background: var(--bg-secondary); color: var(--text-primary);">
                        </div>
                        <div>
                            <label style="font-size: 0.8rem; color: var(--text-secondary);">Username</label>
                            <input type="text" id="email-username" value="${settings.email_username || ''}" placeholder="user@example.com" style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: var(--radius-sm); background: var(--bg-secondary); color: var(--text-primary);">
                        </div>
                        <div>
                            <label style="font-size: 0.8rem; color: var(--text-secondary);">Password</label>
                            <input type="password" id="email-password" value="${settings.email_password || ''}" style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: var(--radius-sm); background: var(--bg-secondary); color: var(--text-primary);">
                        </div>
                        <div>
                            <label style="font-size: 0.8rem; color: var(--text-secondary);">Folder</label>
                            <input type="text" id="email-folder" value="${settings.email_folder || 'INBOX'}" style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: var(--radius-sm); background: var(--bg-secondary); color: var(--text-primary);">
                        </div>
                        <div>
                            <label style="font-size: 0.8rem; color: var(--text-secondary);">Poll Interval (seconds)</label>
                            <input type="number" id="email-interval" value="${settings.email_poll_interval || '300'}" style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: var(--radius-sm); background: var(--bg-secondary); color: var(--text-primary);">
                        </div>
                        <div>
                            <label style="font-size: 0.8rem; color: var(--text-secondary);">Use SSL</label>
                            <select id="email-ssl" style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: var(--radius-sm); background: var(--bg-secondary); color: var(--text-primary);">
                                <option value="true" ${(settings.email_use_ssl || 'true') === 'true' ? 'selected' : ''}>Yes</option>
                                <option value="false" ${settings.email_use_ssl === 'false' ? 'selected' : ''}>No</option>
                            </select>
                        </div>
                    </div>
                    <button class="btn btn-outline btn-sm" id="save-email-btn" style="margin-top: 12px;">Save Email Settings</button>
                </div>

                <!-- Webhook -->
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Webhook Endpoint</span>
                        <span class="badge badge-success">Always Active</span>
                    </div>
                    <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 12px;">
                        HTTP POST endpoint for receiving files from external systems. Requires an API key.
                    </p>
                    <div style="background: var(--bg-tertiary); padding: 12px; border-radius: var(--radius-sm); font-family: var(--font-mono); font-size: 0.85rem; margin-bottom: 8px;">
                        <div style="margin-bottom: 6px;"><strong>File upload:</strong> POST /api/ingest</div>
                        <div style="margin-bottom: 6px;"><strong>Raw EDI:</strong> POST /api/ingest/raw</div>
                        <div><strong>Header:</strong> Authorization: Bearer &lt;your-api-key&gt;</div>
                    </div>
                    <div style="margin-top: 12px;">
                        <strong style="font-size: 0.85rem;">Example (curl):</strong>
                        <pre style="background: var(--bg-tertiary); padding: 12px; border-radius: var(--radius-sm); font-size: 0.8rem; overflow-x: auto; margin-top: 4px;">curl -X POST http://localhost:8000/api/ingest \\
  -H "Authorization: Bearer YOUR_KEY" \\
  -F "file=@remittance.835"</pre>
                    </div>
                    <p style="margin-top: 12px; font-size: 0.85rem; color: var(--text-secondary);">
                        Manage API keys on the <a href="#/api-keys" style="color: var(--accent);">API Keys page</a>.
                    </p>
                </div>
            `;

            this.bindEvents(status);
        } catch (err) {
            content.innerHTML = `<div class="empty-state"><div class="empty-state-text">Error: ${err.message}</div></div>`;
        }
    },

    bindEvents(status) {
        // FTP toggle
        document.getElementById('ftp-toggle-btn').addEventListener('click', async () => {
            try {
                const action = status.ftp.running ? 'stop' : 'start';
                const result = await API.postJSON(`/api/listeners/ftp/${action}`, {});
                Toast.success(result.message);
                setTimeout(() => this.render(), 500);
            } catch (err) {
                Toast.error(err.message);
            }
        });

        // Save FTP settings
        document.getElementById('save-ftp-btn').addEventListener('click', async () => {
            try {
                await API.putJSON('/api/listeners/settings', {
                    sftp_port: document.getElementById('ftp-port').value,
                    sftp_username: document.getElementById('ftp-username').value,
                    sftp_password: document.getElementById('ftp-password').value,
                    sftp_directory: document.getElementById('ftp-directory').value,
                });
                Toast.success('FTP settings saved');
            } catch (err) {
                Toast.error(err.message);
            }
        });

        // Email toggle
        document.getElementById('email-toggle-btn').addEventListener('click', async () => {
            try {
                const action = status.email.running ? 'stop' : 'start';
                const result = await API.postJSON(`/api/listeners/email/${action}`, {});
                Toast.success(result.message);
                setTimeout(() => this.render(), 500);
            } catch (err) {
                Toast.error(err.message);
            }
        });

        // Email check now
        document.getElementById('email-check-btn').addEventListener('click', async () => {
            try {
                const result = await API.postJSON('/api/listeners/email/check', {});
                Toast.success(result.message);
            } catch (err) {
                Toast.error(err.message);
            }
        });

        // Save email settings
        document.getElementById('save-email-btn').addEventListener('click', async () => {
            try {
                await API.putJSON('/api/listeners/settings', {
                    email_imap_host: document.getElementById('email-host').value,
                    email_imap_port: document.getElementById('email-port').value,
                    email_username: document.getElementById('email-username').value,
                    email_password: document.getElementById('email-password').value,
                    email_folder: document.getElementById('email-folder').value,
                    email_poll_interval: document.getElementById('email-interval').value,
                    email_use_ssl: document.getElementById('email-ssl').value,
                });
                Toast.success('Email settings saved');
            } catch (err) {
                Toast.error(err.message);
            }
        });
    },
};
