import { useState, useEffect } from 'react';
import DataEditor from './DataEditor';
import MultiSelect from './MultiSelect';
import { fetchJson } from '../utils/fetchJson';

const CleanPage = () => {
    const [config, setConfig] = useState(null);
    const [previewData, setPreviewData] = useState([]);
    const [timeChangesPreviewData, setTimeChangesPreviewData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isProcessing, setIsProcessing] = useState(false);
    const [processResult, setProcessResult] = useState(null); // { success: bool, outputPath: str }
    const [msg, setMsg] = useState({ text: '', type: '' });

    // Load initial data
    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch config
                const configRes = await fetch('/config/parser');
                const configData = await configRes.json();
                setConfig(configData);

                // Fetch data preview (first 10 rows)
                const { ok: dataOk, data: dataData } = await fetchJson('/data?nrows=10');
                if (dataOk && dataData && dataData.data) {
                    setPreviewData(dataData.data);
                }
            } catch (err) {
                console.error("Failed to load data", err);
                setMsg({ text: 'Failed to load configuration or data.', type: 'error' });
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const handleConfigChange = (key, value) => {
        setConfig(prev => ({
            ...prev,
            [key]: value
        }));
    };

    const saveConfig = async () => {
        try {
            const res = await fetch('/config/parser', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            if (res.ok) {
                setMsg({ text: 'Configuration saved!', type: 'success' });
            } else {
                setMsg({ text: 'Failed to save configuration.', type: 'error' });
            }
        } catch (err) {
            setMsg({ text: `Error: ${err.message}`, type: 'error' });
        }
    };

    const runProcess = async () => {
        setIsProcessing(true);
        setProcessResult(null);
        setMsg({ text: 'Saving config and processing...', type: 'info' });
        try {
            await saveConfig();

            const res = await fetch('/process');
            if (res.ok) {
                // Fetch config again to get updated outputFilePath
                const configRes = await fetch('/config/parser');
                const updatedConfig = await configRes.json();
                setProcessResult({ success: true, outputPath: updatedConfig.outputFilePath || '' });
                setMsg({ text: '', type: '' });
            } else {
                setProcessResult({ success: false });
                setMsg({ text: 'Processing failed.', type: 'error' });
            }
        } catch (err) {
            setProcessResult({ success: false });
            setMsg({ text: `Processing error: ${err.message}`, type: 'error' });
        } finally {
            setIsProcessing(false);
        }
    };

    const previewTimeChanges = async () => {
        setMsg({ text: 'Generating preview...', type: 'info' });
        try {
            await saveConfig();
            const { ok: resOk, data } = await fetchJson('/preview');
            if (resOk && data && data.data && data.data.samples) {
                setTimeChangesPreviewData(data.data.samples);
                setMsg({ text: 'Preview generated successfully!', type: 'success' });
            } else {
                setMsg({ text: 'Failed to generate preview.', type: 'error' });
            }
        } catch (err) {
            setMsg({ text: `Preview error: ${err.message}`, type: 'error' });
        }
    };

    if (loading) return <div>Loading...</div>;
    if (!config) return <div>Error loading configuration.</div>;

    return (
        <div className="clean-page">
            <h2>Operations for Cleaning Input Data</h2>

            {msg.text && <div className={`status-message ${msg.type}`}>{msg.text}</div>}


            <div className="section">
                <div className="flex-between">
                    <h3>Dataset Preview</h3>
                </div>
                <div className="table-container">
                    {previewData && Object.keys(previewData).length > 0 ? (
                        <table>
                            <thead>
                                <tr>
                                    {Object.keys(previewData).map(k => <th key={k}>{k}</th>)}
                                </tr>
                            </thead>
                            <tbody>
                                {/* Since data is column-oriented { col: {0: val, 1: val}, ... }, we iterate over rows (0 to however many keys are in the first column) */}
                                {Object.keys(previewData[Object.keys(previewData)[0]] || {}).map((rowIndex) => (
                                    <tr key={rowIndex}>
                                        {Object.keys(previewData).map(col => (
                                            <td key={col}>{previewData[col][rowIndex]}</td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <p>No data available</p>
                    )}
                </div>
            </div>

            <div className="section config-form-container">
                <h3>Settings</h3>

                <div className="form-group">
                    <label>Input Path (Read-only)</label>
                    <input type="text" value={config.inputPath || ''} readOnly disabled />

                    {config.isDirectory && config.targetFiles && config.targetFiles.length > 0 && (
                        <details style={{ marginTop: '0.5rem' }}>
                            <summary>Files found in input directory</summary>
                            <ul>
                                {config.targetFiles.map(f => <li key={f}>{f}</li>)}
                            </ul>
                        </details>
                    )}
                </div>

                <div className="form-group">
                    <label>File Encoding</label>
                    <select
                        value={config.inputFileEncoding || 'utf-8-sig'}
                        onChange={(e) => handleConfigChange('inputFileEncoding', e.target.value)}
                    >
                        <option value="utf-8-sig">utf-8-sig</option>
                        <option value="ISO-8859-1">ISO-8859-1</option>
                    </select>
                </div>

                <div className="form-group">
                    <label>Output File Path</label>
                    <input
                        type="text"
                        value={config.outputFilePath || ''}
                        onChange={(e) => handleConfigChange('outputFilePath', e.target.value)}
                    />
                </div>

                {config.isDirectory && (
                    <div className="form-group">
                        <label>
                            <input
                                type="checkbox"
                                checked={!!config.concatFiles}
                                onChange={(e) => handleConfigChange('concatFiles', e.target.checked)}
                            /> Concatenate input files
                        </label>
                    </div>
                )}

                <div className="checkbox-grid" style={{ marginBottom: '1rem' }}>
                    {[
                        { key: 'fixTimes', label: 'Fix Times' },
                        { key: 'deleteColumns', label: 'Delete Selected Columns' },
                        { key: 'normalizeHeaders', label: 'Normalize Headers' },
                        { key: 'appendHeaders', label: 'Append Row Value to Headers' },
                        { key: 'dropAppendedRow', label: 'Drop Appended Row' },
                        { key: 'replaceValues', label: 'Replace Row Values' },
                        { key: 'dropDuplicates', label: 'Drop Duplicate Rows' },
                        { key: 'dropEmpty', label: 'Drop Empty Columns' }
                    ].map(({ key, label }) => (
                        <div key={key} className="checkbox-item">
                            <label>
                                <input
                                    type="checkbox"
                                    checked={!!config[key]}
                                    onChange={(e) => handleConfigChange(key, e.target.checked)}
                                /> {label}
                            </label>
                        </div>
                    ))}
                </div>

                <div className="responsive-grid grid-2-col">
                    <div className="form-group">
                        <label>Parsed Time Column Name</label>
                        <input
                            type="text"
                            value={config.parsedColumnName || ''}
                            onChange={(e) => handleConfigChange('parsedColumnName', e.target.value)}
                        />
                    </div>

                    <div className="form-group">
                        <label>Parsed Column Position</label>
                        <input
                            type="number"
                            min="0"
                            value={config.parsedColumnPosition || 0}
                            onChange={(e) => handleConfigChange('parsedColumnPosition', parseInt(e.target.value, 10))}
                        />
                    </div>
                </div>

                <div className="responsive-grid grid-2-col">
                    <div className="form-group">
                        <label>Date Fields</label>
                        <DataEditor
                            data={config.dateFields || {}}
                            onChange={(newData) => handleConfigChange('dateFields', newData)}
                        />
                    </div>
                    <div className="form-group">
                        <label>Time Field</label>
                        <DataEditor
                            data={config.timeField || {}}
                            onChange={(newData) => handleConfigChange('timeField', newData)}
                        />
                    </div>
                    <div className="form-group">
                        <label>Header Values to Replace</label>
                        <DataEditor
                            data={config.headerValuesToReplace || []}
                            columns={['original', 'replacement']}
                            onChange={(newData) => handleConfigChange('headerValuesToReplace', newData)}
                        />
                    </div>
                    <div className="form-group">
                        <label>Row Values to Replace</label>
                        <DataEditor
                            data={config.rowValuesToReplace || []}
                            columns={['original', 'replacement']}
                            onChange={(newData) => handleConfigChange('rowValuesToReplace', newData)}
                        />
                    </div>
                </div>

                <div className="responsive-grid grid-1-col">
                    <div className="form-group">
                        <label>Row to append to Column Headers</label>
                        <input
                            type="number"
                            min="0"
                            value={config.rowForColumnAppend || 0}
                            onChange={(e) => handleConfigChange('rowForColumnAppend', parseInt(e.target.value, 10))}
                        />
                    </div>

                    <div className="form-group">
                        <label>Target Columns for Row Replacement (blank will target all columns)</label>
                        <MultiSelect
                            options={config.fieldNames || []}
                            selected={config.columnsForReplace || []}
                            onChange={(selected) => handleConfigChange('columnsForReplace', selected)}
                            emptyMessage="No columns selected. (Blank targets all)"
                        />
                    </div>

                    <div className="form-group">
                        <label>Columns To Delete</label>
                        <MultiSelect
                            options={config.fieldNames || []}
                            selected={config.columnsToDelete || []}
                            onChange={(selected) => handleConfigChange('columnsToDelete', selected)}
                            emptyMessage="No columns selected."
                        />
                    </div>
                </div>

                <div style={{ marginTop: '1rem' }}>
                    <button onClick={saveConfig}>Save Settings</button>
                </div>
            </div>



            <div className="section">
                <div className="flex-between">
                    <h3>Time Changes Preview</h3>
                    <button type="button" onClick={previewTimeChanges} className="secondary">Preview Time Changes</button>
                </div>
                {timeChangesPreviewData && (Object.keys(timeChangesPreviewData).length > 0 || (Array.isArray(timeChangesPreviewData) && timeChangesPreviewData.length > 0)) && (
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    {Array.isArray(timeChangesPreviewData) ?
                                        Object.keys(timeChangesPreviewData[0] || {}).map(k => <th key={k}>{k}</th>)
                                        : Object.keys(timeChangesPreviewData).map(k => <th key={k}>{k}</th>)
                                    }
                                </tr>
                            </thead>
                            <tbody>
                                {Array.isArray(timeChangesPreviewData) ? (
                                    timeChangesPreviewData.map((row, i) => (
                                        <tr key={i}>
                                            {Object.values(row).map((val, j) => <td key={j}>{val}</td>)}
                                        </tr>
                                    ))
                                ) : (
                                    Object.keys(timeChangesPreviewData[Object.keys(timeChangesPreviewData)[0]] || {}).map((rowIndex) => (
                                        <tr key={rowIndex}>
                                            {Object.keys(timeChangesPreviewData).map(col => (
                                                <td key={col}>{timeChangesPreviewData[col][rowIndex]}</td>
                                            ))}
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            <div className="section">
                <h3>Actions</h3>
                <button className="primary" onClick={runProcess} disabled={isProcessing}>
                    {isProcessing ? 'Processing...' : 'Process File(s)'}
                </button>

                {isProcessing && (
                    <div className="status-message info" style={{ marginTop: '10px' }}>
                        ⏳ Processing file, please wait...
                    </div>
                )}

                {processResult && processResult.success && (
                    <div className="status-message success" style={{ marginTop: '10px' }}>
                        ✅ Processing successful!{processResult.outputPath && (
                            <span> Output written to: <code>{processResult.outputPath}</code></span>
                        )}
                    </div>
                )}

                {processResult && !processResult.success && (
                    <div className="status-message error" style={{ marginTop: '10px' }}>
                        ❌ Processing failed. Check the API logs for details.
                    </div>
                )}
            </div>
        </div>
    );
};

export default CleanPage;
