import { useState } from 'react';

const ConfigForm = ({ onUploadSuccess }) => {
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState('');
    const [status, setStatus] = useState(''); // 'success' or 'error'

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            setFile(e.target.files[0]);
            setMessage('');
            setStatus('');
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!file) {
            setMessage('Please select a file first.');
            setStatus('error');
            return;
        }

        setMessage('Uploading file...');
        setStatus('');

        const formData = new FormData();
        formData.append('file', file);

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
                <div className="form-group" style={{ marginBottom: '1rem' }}>
                    <label htmlFor="fileInput">Choose File:</label>
                    <input
                        id="fileInput"
                        type="file"
                        onChange={handleFileChange}
                        accept=".csv,.nc"
                    />
                </div>

                <div style={{ display: 'flex', gap: '10px', marginBottom: '1rem' }}>
                    <button type="submit" disabled={!file} className="primary">Upload File</button>
                    <button type="button" onClick={handleTestModeSubmit} className="secondary">Test Mode</button>
                </div>
            </form>

            {message && <div className={`status-message ${status}`}>{message}</div>}
        </div>
    );
};

export default ConfigForm;
