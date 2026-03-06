import { useState, useEffect } from 'react';
import { fetchJson } from '../utils/fetchJson';

const BioDataUtilsPage = () => {
    const [parserConfig, setParserConfig] = useState(null);
    const [transformConfig, setTransformConfig] = useState(null);
    const [previewData, setPreviewData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [msg, setMsg] = useState({ text: '', type: '' });

    // Taxonomic Name Matching State
    const [targetColumn, setTargetColumn] = useState('');
    const [taxonMatchResults, setTaxonMatchResults] = useState(null);
    const [isMatching, setIsMatching] = useState(false);
    const [acceptedMatches, setAcceptedMatches] = useState({}); // { originalName: bool }

    // Merge State
    const [transformOutputPath, setTransformOutputPath] = useState('');
    const [isMerging, setIsMerging] = useState(false);

    const dataColumns = previewData ? Object.keys(previewData) : [];

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [parserRes, transformRes, dataRes] = await Promise.all([
                    fetchJson('/config/parser'),
                    fetchJson('/config/transform'),
                    fetchJson('/data?nrows=10'),
                ]);

                if (parserRes.ok) setParserConfig(parserRes.data);
                if (transformRes.ok) {
                    setTransformConfig(transformRes.data);
                    setTransformOutputPath(transformRes.data.transform_output_path || '');
                }
                if (dataRes.ok && dataRes.data && dataRes.data.data) {
                    setPreviewData(dataRes.data.data);
                }
            } catch (err) {
                setMsg({ text: `Failed to load data: ${err.message}`, type: 'error' });
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const handleUpdateInput = async () => {
        setMsg({ text: 'Updating input path...', type: 'info' });
        try {
            const res = await fetch('/config/parser', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ inputPath: parserConfig.inputPath }),
            });
            if (res.ok) {
                setMsg({ text: 'Config updated.', type: 'success' });
                // Refresh data preview
                const dataRes = await fetchJson('/data?nrows=10');
                if (dataRes.ok && dataRes.data && dataRes.data.data) {
                    setPreviewData(dataRes.data.data);
                }
            } else {
                setMsg({ text: 'Failed to update config.', type: 'error' });
            }
        } catch (err) {
            setMsg({ text: `Error: ${err.message}`, type: 'error' });
        }
    };

    const handleMatchTaxa = async () => {
        if (!targetColumn) {
            setMsg({ text: 'Please select a target column first.', type: 'error' });
            return;
        }

        setIsMatching(true);
        setTaxonMatchResults(null);
        setMsg({ text: 'Matching taxonomic names...', type: 'info' });

        try {
            // 1. Update config with target column
            const configRes = await fetch('/config/transform', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_column_for_taxon: targetColumn }),
            });
            if (!configRes.ok) throw new Error('Failed to update config.');

            // 2. Clear accepted matches
            setAcceptedMatches({});

            // 3. Generate preview
            const previewRes = await fetchJson('/preview?preview_type=taxonomic_names');
            if (previewRes.ok && previewRes.data && previewRes.data.data) {
                setTaxonMatchResults(previewRes.data.data);
                setMsg({ text: 'Taxonomic names matched successfully.', type: 'success' });
            } else {
                setMsg({ text: 'Taxonomic name matching failed.', type: 'error' });
            }
        } catch (err) {
            setMsg({ text: `Error: ${err.message}`, type: 'error' });
        } finally {
            setIsMatching(false);
        }
    };

    const handleToggleAccepted = (originalName) => {
        setAcceptedMatches(prev => ({
            ...prev,
            [originalName]: !prev[originalName]
        }));
    };

    const handleAcceptResults = async () => {
        const acceptedValues = Object.keys(acceptedMatches).filter(key => acceptedMatches[key]);

        setMsg({ text: 'Accepting selected results...', type: 'info' });
        try {
            const res = await fetch('/config/transform', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ accepted_taxon_matches: acceptedValues }),
            });
            if (res.ok) {
                setMsg({ text: `Accepted ${acceptedValues.length} matches.`, type: 'success' });
            } else {
                setMsg({ text: 'Failed to update config.', type: 'error' });
            }
        } catch (err) {
            setMsg({ text: `Error: ${err.message}`, type: 'error' });
        }
    };

    const handleMergeTaxa = async () => {
        setIsMerging(true);
        setMsg({ text: 'Merging taxa information...', type: 'info' });
        try {
            // Update output path first
            const configRes = await fetch('/config/transform', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ transform_output_path: transformOutputPath }),
            });
            if (!configRes.ok) throw new Error('Failed to update output path.');

            const res = await fetch('/transform?operation=merge_taxa', {
                method: 'POST',
            });
            if (res.ok) {
                setMsg({ text: 'Success - taxonomic information merged.', type: 'success' });
            } else {
                setMsg({ text: 'Failed to merge taxa information.', type: 'error' });
            }
        } catch (err) {
            setMsg({ text: `Error: ${err.message}`, type: 'error' });
        } finally {
            setIsMerging(false);
        }
    };

    if (loading) return <div>Loading...</div>;

    const taxonPreviewHeaders = taxonMatchResults
        ? ['accepted', 'Original', ...Object.keys(taxonMatchResults[Object.keys(taxonMatchResults)[0]].after || {})]
        : [];

    return (
        <div className="clean-page">
            <h2>Biological Data Utilities</h2>

            {msg.text && <div className={`status-message ${msg.type}`}>{msg.text}</div>}

            {/* Input Config */}
            <div className="section config-form-container">
                <div className="form-group">
                    <label>Input File Path</label>
                    <div style={{ display: 'flex', gap: '10px' }}>
                        <input
                            type="text"
                            style={{ flex: 1 }}
                            value={parserConfig?.inputPath || ''}
                            onChange={e => setParserConfig({ ...parserConfig, inputPath: e.target.value })}
                        />
                        <button onClick={handleUpdateInput}>Update</button>
                    </div>
                </div>
            </div>

            {/* Dataset Preview */}
            {previewData && Object.keys(previewData).length > 0 && (
                <div className="section">
                    <h3>Dataset Preview</h3>
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    {Object.keys(previewData).map(k => <th key={k}>{k}</th>)}
                                </tr>
                            </thead>
                            <tbody>
                                {Object.keys(previewData[Object.keys(previewData)[0]] || {}).map(rowIndex => (
                                    <tr key={rowIndex}>
                                        {Object.keys(previewData).map(col => (
                                            <td key={col}>{previewData[col][rowIndex]}</td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Taxonomic Matching Section */}
            <div className="section config-form-container">
                <h3>Taxonomic Name Matching</h3>
                <p>Match selected column in input data against taxonomic information from WORMS; approve and merge changes into source data.</p>

                <div className="form-group">
                    <label>Select Target Column</label>
                    <select
                        value={targetColumn}
                        onChange={e => setTargetColumn(e.target.value)}
                    >
                        <option value="">-- Select Organism Name Column --</option>
                        {dataColumns.map(col => <option key={col} value={col}>{col}</option>)}
                    </select>
                </div>

                <button
                    className="primary"
                    onClick={handleMatchTaxa}
                    disabled={isMatching}
                >
                    {isMatching ? 'Matching...' : 'Match Taxonomic Names'}
                </button>

                {taxonMatchResults && (
                    <div className="section" style={{ marginTop: '2rem' }}>
                        <h4>Taxonomic Name Preview</h4>
                        <div className="taxon-preview-container">
                            <table>
                                <thead>
                                    <tr>
                                        {taxonPreviewHeaders.map(h => <th key={h}>{h}</th>)}
                                    </tr>
                                </thead>
                                <tbody>
                                    {Object.keys(taxonMatchResults).map(originalName => {
                                        const result = taxonMatchResults[originalName];
                                        const matchType = result.after?.matchType || '';
                                        return (
                                            <tr key={originalName} className={`match-${matchType}`}>
                                                <td>
                                                    <input
                                                        type="checkbox"
                                                        checked={!!acceptedMatches[originalName]}
                                                        onChange={() => handleToggleAccepted(originalName)}
                                                    />
                                                </td>
                                                <td>{result.before}</td>
                                                {Object.values(result.after || {}).map((val, idx) => (
                                                    <td key={idx}>{String(val)}</td>
                                                ))}
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                        <button onClick={handleAcceptResults}>Accept Selected Results</button>
                    </div>
                )}
            </div>

            {/* Merge Section */}
            <div className="section config-form-container">
                <h3>Merge Results</h3>
                <div className="form-group">
                    <label>Output Path for Merge</label>
                    <input
                        type="text"
                        value={transformOutputPath}
                        onChange={e => setTransformOutputPath(e.target.value)}
                        placeholder="path/to/output.csv"
                    />
                </div>
                <button
                    className="primary"
                    onClick={handleMergeTaxa}
                    disabled={isMerging}
                >
                    {isMerging ? 'Merging...' : 'Merge Taxa Information'}
                </button>
            </div>
        </div>
    );
};

export default BioDataUtilsPage;
