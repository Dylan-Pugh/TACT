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

    // ─── Column Splitting State ───────────────────────────────────────────────
    // Rules are held locally only for the duration of an edit session; the config
    // file remains the source of truth and is written before every preview.
    const [splitRules, setSplitRules] = useState([]);
    const [splitPreview, setSplitPreview] = useState(null);
    const [isPreviewingSplit, setIsPreviewingSplit] = useState(false);
    const [splitOutputPath, setSplitOutputPath] = useState('');
    const [isSplitting, setIsSplitting] = useState(false);
    const [splitResult, setSplitResult] = useState(null);

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
                setSplitRules(transform.column_split_rules || []);
                setSplitOutputPath(transform.split_output_path || '');
            } catch (err) {
                setMsg({ text: `Failed to load data: ${err.message}`, type: 'error' });
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    // ─── Transform Config Helper (mirrors CleanPage pattern) ─────────────────
    const handleTransformConfigChange = (key, value) => {
        setTransformConfig(prev => ({ ...prev, [key]: value }));
    };

    // ─── Column Splitting Handlers ────────────────────────────────────────────
    const updateSplitRule = (index, key, value) => {
        setSplitRules(prev => prev.map((rule, i) => (i === index ? { ...rule, [key]: value } : rule)));
    };

    const addSplitRule = () => {
        setSplitRules(prev => [
            ...prev,
            { source_column: '', delimiter: '', output_columns: '', remove_match: true },
        ]);
    };

    const removeSplitRule = (index) => {
        setSplitRules(prev => prev.filter((_, i) => i !== index));
    };

    // Rule order is significant: with overwrite off, the first rule to populate a
    // cell wins, so more specific delimiters must run before more general ones.
    const moveSplitRule = (index, offset) => {
        const target = index + offset;
        if (target < 0 || target >= splitRules.length) return;
        setSplitRules(prev => {
            const next = [...prev];
            [next[index], next[target]] = [next[target], next[index]];
            return next;
        });
    };

    const previewSplitRules = async () => {
        setIsPreviewingSplit(true);
        setSplitPreview(null);
        setMsg({ text: 'Saving rules and generating preview...', type: 'info' });
        try {
            const configRes = await fetch('/config/transform', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ column_split_rules: splitRules }),
            });
            if (!configRes.ok) throw new Error('Config update failed');

            const { ok, data } = await fetchJson('/preview?preview_type=split_fields');
            if (ok && data && data.data) {
                setSplitPreview(data.data);
                setMsg({ text: '', type: '' });
            } else {
                setMsg({ text: 'Failed to generate split preview.', type: 'error' });
            }
        } catch (err) {
            setMsg({ text: `Preview error: ${err.message}`, type: 'error' });
        } finally {
            setIsPreviewingSplit(false);
        }
    };

    const handleSplitColumns = async () => {
        setIsSplitting(true);
        setSplitResult(null);
        setMsg({ text: 'Saving rules and splitting columns...', type: 'info' });
        try {
            const configRes = await fetch('/config/transform', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    column_split_rules: splitRules,
                    split_output_path: splitOutputPath,
                }),
            });
            if (!configRes.ok) throw new Error('Config update failed');

            const params = new URLSearchParams({ operation: 'split_fields' });
            const splitRes = await fetch(`/transform?${params.toString()}`, { method: 'POST' });

            setSplitResult({ success: splitRes.ok });
            setMsg({ text: '', type: '' });
        } catch (err) {
            setSplitResult({ success: false });
            setMsg({ text: `Split error: ${err.message}`, type: 'error' });
        } finally {
            setIsSplitting(false);
        }
    };

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

    // ─── Lookup Upload & Merge ─────────────────────────────────────────────────
    const [lookupFile, setLookupFile] = useState([]);
    const [isUploadingLookup, setIsUploadingLookup] = useState(false);
    const [isMergingLookup, setIsMergingLookup] = useState(false);
    const [lookupUploadResult, setLookupUploadResult] = useState(null);
    const [lookupMergeResult, setLookupMergeResult] = useState(null);

    const handleLookupFileChange = (e) => {
        if (e.target.files && e.target.files.length > 0) {
            setLookupFile(Array.from(e.target.files));
            setLookupUploadResult(null);
        }
    };

    const handleLookupUpload = async () => {
        if (lookupFile.length === 0) return;
        setIsUploadingLookup(true);
        setLookupUploadResult(null);
        setMsg({ text: 'Uploading lookup file...', type: 'info' });
        try {
            const formData = new FormData();
            formData.append('file', lookupFile[0]);
            const res = await fetch('/upload?type=lookup', { method: 'POST', body: formData });
            if (res.ok) {
                // Refresh transform config to get updated lookup_file_path & lookup_field_names
                const configRes = await fetch('/config/transform');
                const configData = await configRes.json();
                setTransformConfig(configData);
                setLookupUploadResult({ success: true });
                setMsg({ text: '', type: '' });
                // Clear the file input so the same file can be re-uploaded
                const fileInput = document.getElementById('lookupFileInput');
                if (fileInput) fileInput.value = '';
                setLookupFile([]);
            } else {
                const err = await res.json().catch(() => ({}));
                setLookupUploadResult({ success: false });
                setMsg({ text: `Upload failed: ${err.message || res.statusText}`, type: 'error' });
            }
        } catch (err) {
            setLookupUploadResult({ success: false });
            setMsg({ text: `Error: ${err.message}`, type: 'error' });
        } finally {
            setIsUploadingLookup(false);
        }
    };

    const handleMergeLookup = async () => {
        setIsMergingLookup(true);
        setLookupMergeResult(null);
        setMsg({ text: 'Saving config and merging...', type: 'info' });
        try {
            const outgoingConfig = {
                lookup_key_column: transformConfig?.lookup_key_column || '',
                target_key_column: transformConfig?.target_key_column || '',
                lookup_value_columns: transformConfig?.lookup_value_columns || [],
                lookup_output_path: transformConfig?.lookup_output_path || '',
            };
            const configRes = await fetch('/config/transform', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(outgoingConfig),
            });
            if (!configRes.ok) throw new Error('Config update failed');

            const mergeRes = await fetch('/transform?operation=merge_lookup', { method: 'POST' });
            if (mergeRes.ok) {
                setLookupMergeResult({ success: true });
                setMsg({ text: '', type: '' });
            } else {
                const errBody = await mergeRes.json().catch(() => ({}));
                setLookupMergeResult({ success: false });
                setMsg({ text: `Lookup merge failed: ${errBody.message || mergeRes.statusText}`, type: 'error' });
            }
        } catch (err) {
            setLookupMergeResult({ success: false });
            setMsg({ text: `Error: ${err.message}`, type: 'error' });
        } finally {
            setIsMergingLookup(false);
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

            {/* ── Section 3: Lookup Merge ───────────────────────────────────── */}
            <div className="section config-form-container">
                <h3>Lookup Merge</h3>
                <p style={{ marginBottom: '1rem' }}>
                    Join an external lookup table to the active dataset. Rows are matched
                    on a key column.
                </p>

                {/* Step 1: Upload lookup file */}
                <div className="form-group">
                    <label>Step 1 — Upload Lookup Table (CSV)</label>
                    <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
                        <input
                            id="lookupFileInput"
                            type="file"
                            accept=".csv"
                            onChange={handleLookupFileChange}
                        />
                        <button
                            className="secondary"
                            onClick={handleLookupUpload}
                            disabled={isUploadingLookup || lookupFile.length === 0}
                        >
                            {isUploadingLookup ? 'Uploading...' : 'Upload'}
                        </button>
                    </div>
                    {lookupUploadResult && lookupUploadResult.success && (
                        <div className="status-message success" style={{ marginTop: '6px' }}>
                            ✅ Lookup file uploaded — columns loaded.
                        </div>
                    )}
                    {lookupUploadResult && !lookupUploadResult.success && (
                        <div className="status-message error" style={{ marginTop: '6px' }}>
                            ❌ Upload failed. Check logs for details.
                        </div>
                    )}
                    {transformConfig?.lookup_file_path && (
                        <div style={{ marginTop: '6px', fontSize: '0.85em', color: '#888' }}>
                            Active lookup file: <code>{transformConfig.lookup_file_path}</code>
                        </div>
                    )}
                </div>

                {/* Step 2: Configure keys */}
                <div className="responsive-grid grid-2-col">
                    <div className="form-group">
                        <label>Step 2a — Key Column in Lookup Table</label>
                        <select
                            value={transformConfig?.lookup_key_column || ''}
                            onChange={e => handleTransformConfigChange('lookup_key_column', e.target.value)}
                        >
                            <option value="">-- Select --</option>
                            {(transformConfig?.lookup_field_names || []).map(c => (
                                <option key={c} value={c}>{c}</option>
                            ))}
                        </select>
                    </div>
                    <div className="form-group">
                        <label>Step 2b — Key Column in Target Dataset</label>
                        <select
                            value={transformConfig?.target_key_column || ''}
                            onChange={e => handleTransformConfigChange('target_key_column', e.target.value)}
                        >
                            <option value="">-- Select --</option>
                            {dataColumns.map(c => (
                                <option key={c} value={c}>{c}</option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Step 3: Columns to copy */}
                <div className="form-group">
                    <label>Step 3 — Columns to Copy from Lookup Table</label>
                    <MultiSelect
                        options={transformConfig?.lookup_field_names || []}
                        selected={transformConfig?.lookup_value_columns || []}
                        onChange={selected => handleTransformConfigChange('lookup_value_columns', selected)}
                        onSelectAll={() => handleTransformConfigChange('lookup_value_columns', [...(transformConfig?.lookup_field_names || [])])}
                        emptyMessage="Upload a lookup file first to populate column list."
                    />
                </div>

                {/* Output path */}
                <div className="form-group">
                    <label>Output Path</label>
                    <input
                        type="text"
                        value={transformConfig?.lookup_output_path || ''}
                        placeholder="path/to/merged_output.csv"
                        onChange={e => handleTransformConfigChange('lookup_output_path', e.target.value)}
                    />
                </div>

                <button className="primary" onClick={handleMergeLookup} disabled={isMergingLookup}>
                    {isMergingLookup ? 'Merging...' : 'Merge Lookup'}
                </button>

                {isMergingLookup && (
                    <div className="status-message info" style={{ marginTop: '10px' }}>
                        ⏳ Merging lookup table, please wait...
                    </div>
                )}
                {lookupMergeResult && lookupMergeResult.success && (
                    <div className="status-message success" style={{ marginTop: '10px' }}>
                        ✅ Success — lookup merged.
                    </div>
                )}
                {lookupMergeResult && !lookupMergeResult.success && (
                    <div className="status-message error" style={{ marginTop: '10px' }}>
                        ❌ Merge failed. Check the API logs for details.
                    </div>
                )}
            </div>

            {/* ── Section 4: Column Splitting ───────────────────────────────── */}
            <div className="section config-form-container">
                <h3>Column Splitting</h3>
                <p style={{ marginBottom: '1rem' }}>
                    Extract values out of a field into other columns using a delimiter or
                    regex. Rules run top to bottom, and the first rule to fill a cell keeps
                    it — so put more specific delimiters (e.g. <code>post larvae</code>)
                    above more general ones (e.g. <code>larvae</code>).
                </p>

                {splitRules.map((rule, index) => (
                    <div
                        key={index}
                        className="form-group"
                        style={{ border: '1px solid var(--border-color, #ccc)', borderRadius: '4px', padding: '10px', marginBottom: '10px' }}
                    >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                            <strong>Rule {index + 1}</strong>
                            <div style={{ display: 'flex', gap: '6px' }}>
                                <button type="button" className="secondary" onClick={() => moveSplitRule(index, -1)} disabled={index === 0}>↑</button>
                                <button type="button" className="secondary" onClick={() => moveSplitRule(index, 1)} disabled={index === splitRules.length - 1}>↓</button>
                                <button type="button" className="secondary" onClick={() => removeSplitRule(index)}>Remove</button>
                            </div>
                        </div>

                        <div className="responsive-grid grid-2-col">
                            <div className="form-group">
                                <label>Source Column</label>
                                <input
                                    type="text"
                                    value={rule.source_column || ''}
                                    onChange={e => updateSplitRule(index, 'source_column', e.target.value)}
                                    placeholder="taxon"
                                />
                            </div>
                            <div className="form-group">
                                <label>Delimiter / Regex</label>
                                <input
                                    type="text"
                                    value={rule.delimiter || ''}
                                    onChange={e => updateSplitRule(index, 'delimiter', e.target.value)}
                                    placeholder="\blarvae\b"
                                />
                            </div>
                            <div className="form-group">
                                <label>Output Columns (comma separated)</label>
                                <input
                                    type="text"
                                    value={Array.isArray(rule.output_columns) ? rule.output_columns.join(', ') : (rule.output_columns || '')}
                                    onChange={e => {
                                        const parts = e.target.value.split(',').map(s => s.trim()).filter(Boolean);
                                        updateSplitRule(index, 'output_columns', parts.length > 1 ? parts : e.target.value);
                                    }}
                                    placeholder="taxon_stage"
                                />
                            </div>
                            <div className="form-group">
                                <label>Literal Value (optional — overrides extracted text)</label>
                                <input
                                    type="text"
                                    value={rule.value || ''}
                                    onChange={e => updateSplitRule(index, 'value', e.target.value || null)}
                                    placeholder="V-VI"
                                />
                            </div>
                        </div>

                        <div style={{ display: 'flex', gap: '18px', flexWrap: 'wrap' }}>
                            <label><input type="checkbox" checked={!!rule.remove_match} onChange={e => updateSplitRule(index, 'remove_match', e.target.checked)} /> Remove match from source</label>
                            <label><input type="checkbox" checked={!!rule.overwrite} onChange={e => updateSplitRule(index, 'overwrite', e.target.checked)} /> Overwrite existing values</label>
                            <label><input type="checkbox" checked={!!rule.case_sensitive} onChange={e => updateSplitRule(index, 'case_sensitive', e.target.checked)} /> Case sensitive</label>
                        </div>
                    </div>
                ))}

                <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                    <button type="button" className="secondary" onClick={addSplitRule}>Add Rule</button>
                    <button
                        type="button"
                        className="primary"
                        onClick={previewSplitRules}
                        disabled={isPreviewingSplit || splitRules.length === 0}
                    >
                        {isPreviewingSplit ? 'Generating...' : 'Preview Split Rules'}
                    </button>
                </div>

                <div className="form-group" style={{ marginTop: '1.5rem' }}>
                    <label>Output Path for Split</label>
                    <input
                        type="text"
                        value={splitOutputPath}
                        onChange={e => setSplitOutputPath(e.target.value)}
                        placeholder="path/to/output.csv"
                    />
                </div>
                <button
                    type="button"
                    className="primary"
                    onClick={handleSplitColumns}
                    disabled={isSplitting || splitRules.length === 0 || !splitOutputPath}
                >
                    {isSplitting ? 'Splitting...' : 'Split Columns'}
                </button>

                {isSplitting && (
                    <div className="status-message info" style={{ marginTop: '10px' }}>
                        ⏳ Splitting columns, please wait...
                    </div>
                )}
                {splitResult && splitResult.success && (
                    <div className="status-message success" style={{ marginTop: '10px' }}>
                        ✅ Success — output written to {splitOutputPath}
                    </div>
                )}
                {splitResult && !splitResult.success && (
                    <div className="status-message error" style={{ marginTop: '10px' }}>
                        ❌ Split failed. Check the API logs for details.
                    </div>
                )}

                {splitPreview && splitPreview.rule_summary && (
                    <div className="section" style={{ marginTop: '1.5rem' }}>
                        <h4>Rule Summary ({splitPreview.total_rows} rows)</h4>
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        <th>#</th><th>Source</th><th>Delimiter</th><th>Mode</th>
                                        <th>Outputs</th><th>Matched</th><th>Changed</th><th>Shadowed</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {splitPreview.rule_summary.map(entry => (
                                        <tr key={entry.rule_index}>
                                            <td>{entry.rule_index}</td>
                                            <td>{entry.source_column}</td>
                                            <td><code>{entry.delimiter}</code></td>
                                            <td>{entry.mode || '—'}</td>
                                            <td>{(entry.output_columns || []).join(', ')}</td>
                                            <td>{entry.matched_rows}</td>
                                            <td>{entry.changed_rows}</td>
                                            <td>{entry.shadowed_rows}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        {splitPreview.rule_summary.filter(e => e.error).map(e => (
                            <div key={`err-${e.rule_index}`} className="status-message error" style={{ marginTop: '10px' }}>
                                ❌ Rule {e.rule_index}: {e.error}
                            </div>
                        ))}
                        {splitPreview.rule_summary.filter(e => !e.error && e.matched_rows === 0).map(e => (
                            <div key={`nomatch-${e.rule_index}`} className="status-message error" style={{ marginTop: '10px' }}>
                                ⚠️ Rule {e.rule_index} (<code>{e.delimiter}</code>) matched no rows — check the delimiter.
                            </div>
                        ))}
                        {splitPreview.rule_summary.filter(e => e.shadowed_rows > 0).map(e => (
                            <div key={`shadow-${e.rule_index}`} className="status-message error" style={{ marginTop: '10px' }}>
                                ⚠️ Rule {e.rule_index} (<code>{e.delimiter}</code>) matched {e.matched_rows} rows but
                                changed nothing in {e.shadowed_rows} of them — an earlier rule already filled those
                                destinations. Move this rule up, or enable Overwrite.
                            </div>
                        ))}
                    </div>
                )}

                {splitPreview && splitPreview.samples && splitPreview.samples.length > 0 && (
                    <div className="section" style={{ marginTop: '1.5rem' }}>
                        <h4>Sample Transformations</h4>
                        <p style={{ marginBottom: '0.5rem' }}>
                            One example per distinct input shape, so structurally different
                            matches (end-of-string vs. mid-string) are each shown.
                        </p>
                        <div className="table-container">
                            <table>
                                <thead>
                                    <tr>
                                        {Object.keys(splitPreview.samples[0]).map(k => <th key={k}>{k}</th>)}
                                    </tr>
                                </thead>
                                <tbody>
                                    {splitPreview.samples.map((sample, i) => (
                                        <tr key={i}>
                                            {Object.keys(splitPreview.samples[0]).map(col => (
                                                <td key={col}>{sample[col] === null || sample[col] === undefined ? '—' : String(sample[col])}</td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default TransformPage;
