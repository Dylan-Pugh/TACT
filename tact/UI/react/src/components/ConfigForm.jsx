import { useState } from 'react';

const ConfigForm = ({ onUploadSuccess }) => {
    const [files, setFiles] = useState([]);
    const [folderMode, setFolderMode] = useState(false);
    const [message, setMessage] = useState('');
    const [status, setStatus] = useState(''); // 'success' or 'error'

    const toggleFolderMode = () => {
        setFiles([]);
        setFolderMode(prev => !prev);
    };

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            setFiles(Array.from(e.target.files));
            setMessage('');
            setStatus('');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (files.length === 0) {
            setMessage('Please select a file or directory first.');
            setStatus('error');
            return;
        }

        setMessage('Uploading...');
        setStatus('');

        const formData = new FormData();
        files.forEach(file => {
            formData.append('file', file);
        });

        try {
            // Send file to /upload endpoint
            // Using a relative path which Nginx handles
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                setMessage('File uploaded and config updated successfully.');
                setStatus('success');
                // Allow a brief moment for the user to see success before redirecting, or redirect immediately
                setTimeout(() => {
                    if (onUploadSuccess) onUploadSuccess();
                }, 1000);
            } else {
                const errorData = await response.json().catch(() => ({}));
                setMessage(`Failed to upload: ${errorData.message || response.statusText}`);
                setStatus('error');
            }
        } catch (error) {
            setMessage(`Error: ${error.message}`);
            setStatus('error');
        }
    };

    const handleTestModeSubmit = async () => {
        setMessage('Updating config for test mode...');
        setStatus('');
        const targetPath = 'tact/testing/testData/TACT_test.csv';

        try {
            const response = await fetch('/config/parser', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    inputPath: targetPath,
                    pathForPreview: targetPath
                })
            });

            if (response.ok) {
                setMessage(`Test Mode activated. Path is: ${targetPath}`);
                setStatus('success');
                setTimeout(() => {
                    if (onUploadSuccess) onUploadSuccess();
                }, 1000);
            } else {
                setMessage(`Failed to update config for test mode.`);
                setStatus('error');
            }
        } catch (error) {
            setMessage(`Error: ${error.message}`);
            setStatus('error');
        }
    };

    return (
        <div className="config-form-container">
            <h2>Upload Input File(s)</h2>
            <p className="description">
                Select target .csv or directory.
            </p>

            <form onSubmit={handleSubmit}>
                {/* Mode selector */}
                <div style={{ display: 'flex', gap: '10px', marginBottom: '0.75rem' }}>
                    <button
                        type="button"
                        className={!folderMode ? 'primary' : 'secondary'}
                        onClick={() => { setFiles([]); setFolderMode(false); }}
                    >
                        File Select
                    </button>
                    <button
                        type="button"
                        className={folderMode ? 'primary' : 'secondary'}
                        onClick={() => { setFiles([]); setFolderMode(true); }}
                    >
                        Folder Select
                    </button>
                </div>

                <div className="form-group" style={{ marginBottom: '1rem' }}>
                    <label htmlFor="fileInput">
                        {folderMode ? 'Choose folder:' : 'Choose file(s):'}
                    </label>
                    <input
                        key={folderMode ? 'folder' : 'file'}
                        id="fileInput"
                        type="file"
                        onChange={handleFileChange}
                        {...(folderMode
                            ? { webkitdirectory: 'true', directory: 'true' }
                            : { accept: '.csv,.nc', multiple: true }
                        )}
                    />
                </div>

                <div style={{ display: 'flex', gap: '10px', marginBottom: '1rem', alignItems: 'center' }}>
                    <button type="submit" disabled={files.length === 0} className="primary">Upload</button>
                    <button type="button" onClick={handleTestModeSubmit} className="secondary">Test Mode</button>
                </div>

                {files.length > 1 && (
                    <div style={{ marginBottom: '1rem', padding: '10px', border: '1px solid #ccc', borderRadius: '4px', backgroundColor: '#f9f9f9' }}>
                        <h4 style={{ margin: '0 0 10px 0', fontSize: '0.9em', color: '#333' }}>Selected Files ({files.length}):</h4>
                        <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '0.85em', maxHeight: '150px', overflowY: 'auto', color: '#555', fontFamily: 'monospace' }}>
                            {files.map((f, i) => (
                                <li key={i}>{f.webkitRelativePath || f.name}</li>
                            ))}
                        </ul>
                    </div>
                )}
            </form>

            {message && <div className={`status-message ${status}`}>{message}</div>}
        </div>
    );
};

export default ConfigForm;
