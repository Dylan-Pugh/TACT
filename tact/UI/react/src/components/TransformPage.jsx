import { useState, useEffect } from 'react';
import MultiSelect from './MultiSelect';
import DataEditor from './DataEditor';
import { fetchJson } from '../utils/fetchJson';

const TransformPage = () => {
    const [parserConfig, setParserConfig] = useState(null);
    const [transformConfig, setTransformConfig] = useState(null);
    const [previewData, setPreviewData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [msg, setMsg] = useState({ text: '', type: '' });

    // ─── Row Enumeration / Pivot State ────────────────────────────────────────
    const [mode, setMode] = useState('enumerate_columns');
    const [targetDataColumns, setTargetDataColumns] = useState([]);
    const [pivotColumn, setPivotColumn] = useState('');
    const [pivotValueColumn, setPivotValueColumn] = useState('');
    const [resultsColumn, setResultsColumn] = useState('');
    const [transformOutputPath, setTransformOutputPath] = useState('');
    const [dropUnits, setDropUnits] = useState(false);
    const [columnsFromUnits, setColumnsFromUnits] = useState(false);
    const [dropEmptyRecords, setDropEmptyRecords] = useState(false);
    const [genUUID, setGenUUID] = useState(false);
    const [splitFields, setSplitFields] = useState(false);
    const [setOccurrenceStatus, setSetOccurrenceStatus] = useState(false);
    const [matchColVariants, setMatchColVariants] = useState(false);
    const [primaryUnits, setPrimaryUnits] = useState('');
    const [altUnits, setAltUnits] = useState('');
    const [constants, setConstants] = useState({ constant_key: 'constant_value' });
    const [isFlipping, setIsFlipping] = useState(false);
    const [flipResult, setFlipResult] = useState(null);

    // ─── Row Combination State ─────────────────────────────────────────────────
    const [matchColumns, setMatchColumns] = useState([]);
    const [appendPrefix, setAppendPrefix] = useState('');
    const [regexPattern, setRegexPattern] = useState('');
    const [regexError, setRegexError] = useState('');
    const [combineOutputPath, setCombineOutputPath] = useState('');
    const [isCombining, setIsCombining] = useState(false);
    const [combineResult, setCombineResult] = useState(null);

    const dataColumns = previewData ? Object.keys(previewData) : [];

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [parserRes, transformRes, dataRes] = await Promise.all([
                    fetchJson('/config/parser'),
                    fetchJson('/config/transform'),
                    fetchJson('/data?nrows=10'),
                ]);
                const parser = parserRes.data;
                const transform = transformRes.data;
                const dataJson = dataRes.data;

                setParserConfig(parser);
                setTransformConfig(transform);

                if (dataJson && dataJson.data) {
                    setPreviewData(dataJson.data);
                }

                // Initialize form state from configs
                setResultsColumn(transform.results_column || '');
                setTransformOutputPath(transform.transform_output_path || '');
                setDropUnits(!!transform.drop_units);
                setColumnsFromUnits(!!transform.columns_from_units);
                setDropEmptyRecords(!!transform.drop_empty_records);
                setGenUUID(!!transform.gen_UUID);
                setSplitFields(!!transform.split_fields);
                setSetOccurrenceStatus(!!transform.set_occurrence_status);
                setMatchColVariants(!!transform.match_col_variants);
                setPrimaryUnits(transform.primary_units || '');
                setAltUnits(transform.alt_units || '');
                setConstants(transform.constants || { constant_key: 'constant_value' });
            } catch (err) {
                setMsg({ text: `Failed to load data: ${err.message}`, type: 'error' });
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const handleRegexChange = (val) => {
        setRegexPattern(val);
        if (val) {
            try {
                new RegExp(val);
                setRegexError('');
            } catch (e) {
                setRegexError(`Invalid regex: ${e.message}`);
            }
        } else {
            setRegexError('');
        }
    };

    const handleFlip = async () => {
        setIsFlipping(true);
        setFlipResult(null);
        setMsg({ text: 'Saving config and transforming...', type: 'info' });
        try {
            const outgoingConfig = {
                target_data_columns: targetDataColumns,
                pivot_column: pivotColumn,
                pivot_value_column: pivotValueColumn,
                results_column: resultsColumn,
                transform_output_path: transformOutputPath,
                drop_units: dropUnits,
                columns_from_units: columnsFromUnits,
                drop_empty_records: dropEmptyRecords,
                split_fields: splitFields,
                set_occurrence_status: setOccurrenceStatus,
                match_col_variants: matchColVariants,
                primary_units: primaryUnits,
                alt_units: altUnits,
                gen_UUID: genUUID,
                constants: constants,
            };
            const configRes = await fetch('/config/transform', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(outgoingConfig),
            });
            if (!configRes.ok) throw new Error('Config update failed');

            const params = new URLSearchParams({ operation: mode });
            const flipRes = await fetch(`/transform?${params.toString()}`, { method: 'POST' });

            if (flipRes.ok) {
                setFlipResult({ success: true });
                setMsg({ text: '', type: '' });
            } else {
                setFlipResult({ success: false });
                setMsg({ text: 'Transform failed.', type: 'error' });
            }
        } catch (err) {
            setFlipResult({ success: false });
            setMsg({ text: `Error: ${err.message}`, type: 'error' });
        } finally {
            setIsFlipping(false);
        }
    };

    const handleCombineRows = async () => {
        setIsCombining(true);
        setCombineResult(null);
        setMsg({ text: 'Saving config and combining rows...', type: 'info' });
        try {
            const outgoingConfig = {
                match_columns: matchColumns,
                append_prefix: appendPrefix,
                combine_output_path: combineOutputPath,
            };
            if (regexPattern && !regexError) {
                outgoingConfig.match_pattern = regexPattern;
            }
            const configRes = await fetch('/config/transform', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(outgoingConfig),
            });
            if (!configRes.ok) throw new Error('Config update failed');

            const combineRes = await fetch('/transform?operation=combine_rows', { method: 'POST' });
            if (combineRes.ok) {
                setCombineResult({ success: true });
                setMsg({ text: '', type: '' });
            } else {
                setCombineResult({ success: false });
                setMsg({ text: 'Row combination failed.', type: 'error' });
            }
        } catch (err) {
            setCombineResult({ success: false });
            setMsg({ text: `Error: ${err.message}`, type: 'error' });
        } finally {
            setIsCombining(false);
        }
    };

    if (loading) return <div>Loading...</div>;

    return (
        <div className="clean-page">
            <h2>Operations for Transforming a Dataset</h2>

            {msg.text && <div className={`status-message ${msg.type}`}>{msg.text}</div>}

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

            {/* ── Section 1: Row Enumeration / Pivoting ────────────────────── */}
            <div className="section config-form-container">
                <h3>Row Enumeration Or Pivoting (Flipping)</h3>
                <p style={{ marginBottom: '1rem' }}>
                    Extract data in the target columns into discrete records (rows) OR
                    create new columns from values, and map to another set of values (pivot table).
                    Data in other columns will remain unchanged.

                    You may also define constant values which will be added to every extracted row.
                </p>

                {/* Mode Radio */}
                <div className="form-group">
                    <label>Transformation Mode</label>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        <label style={{ fontWeight: 'normal' }}>
                            <input
                                type="radio"
                                name="mode"
                                value="enumerate_columns"
                                checked={mode === 'enumerate_columns'}
                                onChange={() => setMode('enumerate_columns')}
                                style={{ marginRight: '6px' }}
                            />
                            Enumerate (flip columns into rows)
                        </label>
                        <label style={{ fontWeight: 'normal' }}>
                            <input
                                type="radio"
                                name="mode"
                                value="pivot_columns"
                                checked={mode === 'pivot_columns'}
                                onChange={() => setMode('pivot_columns')}
                                style={{ marginRight: '6px' }}
                            />
                            Pivot (extract values in one column to create new columns)
                        </label>
                    </div>
                </div>

                {/* Target columns - enumerate only */}
                <div className="form-group" style={{ opacity: mode !== 'enumerate_columns' ? 0.4 : 1 }}>
                    <label>Select Target Columns</label>
                    <MultiSelect
                        options={dataColumns}
                        selected={targetDataColumns}
                        onChange={setTargetDataColumns}
                        onSelectAll={() => setTargetDataColumns([...dataColumns])}
                        emptyMessage="No columns selected."
                    />
                </div>

                {/* Pivot selects - pivot only */}
                <div className="responsive-grid grid-2-col" style={{ opacity: mode !== 'pivot_columns' ? 0.4 : 1 }}>
                    <div className="form-group">
                        <label>Column to Flip/Pivot (values become new columns)</label>
                        <select
                            value={pivotColumn}
                            onChange={e => setPivotColumn(e.target.value)}
                            disabled={mode !== 'pivot_columns'}
                        >
                            <option value="">-- Select --</option>
                            {dataColumns.map(c => <option key={c} value={c}>{c}</option>)}
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Value Column (values fill new columns)</label>
                        <select
                            value={pivotValueColumn}
                            onChange={e => setPivotValueColumn(e.target.value)}
                            disabled={mode !== 'pivot_columns'}
                        >
                            <option value="">-- Select --</option>
                            {dataColumns.filter(c => c !== pivotColumn).map(c => <option key={c} value={c}>{c}</option>)}
                        </select>
                    </div>
                </div>

                {/* Checkboxes */}
                <div className="checkbox-grid" style={{ marginBottom: '1rem' }}>
                    {[
                        { key: 'dropUnits', label: 'Drop first row (units)', state: dropUnits, set: setDropUnits, disabled: false, title: '' },
                        { key: 'columnsFromUnits', label: 'Create new columns from units', state: columnsFromUnits, set: setColumnsFromUnits, disabled: false, title: '' },
                        { key: 'dropEmptyRecords', label: 'Drop records with a value of NaN or <= 0 in target columns', state: dropEmptyRecords, set: setDropEmptyRecords, disabled: false, title: '' },
                        { key: 'genUUID', label: 'Generate UUID for each record', state: genUUID, set: setGenUUID, disabled: false, title: '' },
                        { key: 'splitFields', label: 'Split input column into multiple columns', state: splitFields, set: setSplitFields, disabled: mode !== 'enumerate_columns', title: '' },
                        { key: 'setOccurrenceStatus', label: 'Set occurrence status (present/absent) for each record', state: setOccurrenceStatus, set: setSetOccurrenceStatus, disabled: mode !== 'enumerate_columns', title: '' },
                        { key: 'matchColVariants', label: 'Match column variants', state: matchColVariants, set: setMatchColVariants, disabled: false, title: 'If true, values from similar columns will be added to enumerated rows, and assigned the units specified below.' },
                    ].map(({ key, label, state, set, disabled, title }) => (
                        <div key={key} className="checkbox-item" style={{ opacity: disabled ? 0.4 : 1 }}>
                            <label style={{ fontWeight: 'normal' }} title={title || undefined}>
                                <input
                                    type="checkbox"
                                    checked={state}
                                    disabled={disabled}
                                    onChange={e => set(e.target.checked)}
                                    title={title || undefined}
                                /> {label}{title && <span style={{ marginLeft: '4px', color: '#666', cursor: 'help' }} title={title}>ⓘ</span>}
                            </label>
                        </div>
                    ))}
                </div>

                {/* Match column variants preview */}
                {matchColVariants && (
                    <div className="section" style={{ marginBottom: '1rem' }}>
                        <h3>Matched Column Preview</h3>
                        {(() => {
                            const effectiveCols = targetDataColumns.length > 0 ? targetDataColumns : dataColumns;
                            return (
                                <div className="table-container">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>Target Column</th>
                                                <th>Matched Variants</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {effectiveCols.map(col => {
                                                const variants = dataColumns.filter(c => c !== col && c.includes(col));
                                                return (
                                                    <tr key={col}>
                                                        <td>{col}</td>
                                                        <td>{variants.length > 0 ? variants.join(', ') : <em style={{ color: '#888' }}>(none)</em>}</td>
                                                    </tr>
                                                );
                                            })}
                                        </tbody>
                                    </table>
                                </div>
                            );
                        })()}
                    </div>
                )}

                {/* Constants editor */}
                <div className="form-group">
                    <label>Define Constants (optional — added to every enumerated row)</label>
                    <DataEditor
                        data={constants}
                        onChange={setConstants}
                    />
                </div>

                {/* Units */}
                <div className="responsive-grid grid-2-col">
                    <div className="form-group">
                        <label>Units to Apply to Values from Target Column</label>
                        <input type="text" value={primaryUnits} onChange={e => setPrimaryUnits(e.target.value)} />
                    </div>
                    <div className="form-group" style={{ opacity: !matchColVariants ? 0.4 : 1 }}>
                        <label>Units to Apply to Values from Column Variants</label>
                        <input type="text" value={altUnits} onChange={e => setAltUnits(e.target.value)} disabled={!matchColVariants} />
                    </div>
                </div>

                {/* Results column & output */}
                <div className="responsive-grid grid-2-col" style={{ opacity: mode !== 'enumerate_columns' ? 0.4 : 1 }}>
                    <div className="form-group">
                        <label>Column Name for Results</label>
                        <input type="text" value={resultsColumn} onChange={e => setResultsColumn(e.target.value)} disabled={mode !== 'enumerate_columns'} />
                    </div>
                </div>
                <div className="form-group">
                    <label>Output Path</label>
                    <input type="text" value={transformOutputPath} onChange={e => setTransformOutputPath(e.target.value)} />
                </div>

                <button className="primary" onClick={handleFlip} disabled={isFlipping}>
                    {isFlipping ? 'Processing...' : 'Flip It!'}
                </button>

                {isFlipping && (
                    <div className="status-message info" style={{ marginTop: '10px' }}>
                        ⏳ Transforming dataset, please wait...
                    </div>
                )}
                {flipResult && flipResult.success && (
                    <div className="status-message success" style={{ marginTop: '10px' }}>
                        ✅ Success — dataset flipped!
                    </div>
                )}
                {flipResult && !flipResult.success && (
                    <div className="status-message error" style={{ marginTop: '10px' }}>
                        ❌ Failed to flip dataset. Check the API logs for details.
                    </div>
                )}
            </div>

            {/* ── Section 2: Row Combination ───────────────────────────────── */}
            <div className="section config-form-container">
                <h3>Row Combination</h3>
                <p style={{ marginBottom: '1rem' }}>
                    Find records that share 1–n column values and combine them into a single row.
                    Only one copy of duplicate values will be retained, and unique values will be added under additional columns.
                </p>

                <div className="form-group">
                    <label>Select Columns for Match</label>
                    <MultiSelect
                        options={dataColumns}
                        selected={matchColumns}
                        onChange={setMatchColumns}
                        onSelectAll={() => setMatchColumns([...dataColumns])}
                        emptyMessage="No columns selected."
                    />
                </div>

                <div className="form-group">
                    <label>Prefix for Added Columns</label>
                    <input type="text" value={appendPrefix} onChange={e => setAppendPrefix(e.target.value)} />
                </div>

                <div className="form-group">
                    <label>Optional: Regex Pattern for Grouping (applies to match columns)</label>
                    <input
                        type="text"
                        value={regexPattern}
                        placeholder="e.g. ^[^_]+ for date before first underscore"
                        onChange={e => handleRegexChange(e.target.value)}
                    />
                    {regexError && <div className="status-message error" style={{ marginTop: '5px' }}>{regexError}</div>}
                    {regexPattern && !regexError && <div className="status-message success" style={{ marginTop: '5px' }}>Valid regex</div>}
                </div>

                <div className="form-group">
                    <label>Output Path</label>
                    <input
                        type="text"
                        value={combineOutputPath}
                        placeholder="path/to/output.csv"
                        onChange={e => setCombineOutputPath(e.target.value)}
                    />
                </div>

                <button className="primary" onClick={handleCombineRows} disabled={isCombining}>
                    {isCombining ? 'Processing...' : 'Combine Rows!'}
                </button>

                {isCombining && (
                    <div className="status-message info" style={{ marginTop: '10px' }}>
                        ⏳ Combining rows, please wait...
                    </div>
                )}
                {combineResult && combineResult.success && (
                    <div className="status-message success" style={{ marginTop: '10px' }}>
                        ✅ Success — rows combined!
                    </div>
                )}
                {combineResult && !combineResult.success && (
                    <div className="status-message error" style={{ marginTop: '10px' }}>
                        ❌ Failed to combine rows. Check the API logs for details.
                    </div>
                )}
            </div>
        </div>
    );
};

export default TransformPage;
