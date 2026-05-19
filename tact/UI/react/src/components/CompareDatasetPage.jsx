import { useState, useEffect } from 'react';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';
import MultiSelect from './MultiSelect';
import DataEditor from './DataEditor';
import { fetchJson } from '../utils/fetchJson';
import { exportToCsv } from '../utils/exportToCsv';

function CompareDatasetPage() {
    // --- Config state ---
    const [keyColumns, setKeyColumns] = useState([]);
    const [compareColumns, setCompareColumns] = useState([]);
    const [excludeColumns, setExcludeColumns] = useState([]);
    const [tolerances, setTolerances] = useState({});
    const [defaultTolerance, setDefaultTolerance] = useState('');
    const [label1, setLabel1] = useState('Dataset 1');
    const [label2, setLabel2] = useState('Dataset 2');
    const [maxDiffRows, setMaxDiffRows] = useState(500);

    // --- Dataset info ---
    const [primaryFilePath, setPrimaryFilePath] = useState('');
    const [dataset1Columns, setDataset1Columns] = useState([]);
    const [dataset2FieldNames, setDataset2FieldNames] = useState([]);
    const [dataset2Path, setDataset2Path] = useState('');

    // --- Upload state ---
    const [compareFile, setCompareFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);

    // --- Run state ---
    const [isRunning, setIsRunning] = useState(false);
    const [results, setResults] = useState(null);
    const [msg, setMsg] = useState({ text: '', type: '' });
    const [diffColFilter, setDiffColFilter] = useState(null); // null = all columns

    // Shared columns (intersection of both datasets, minus already-selected key columns)
    const sharedColumns = dataset1Columns.filter(c => dataset2FieldNames.includes(c));
    const availableKeyColumns = sharedColumns;
    const availableCompareColumns = sharedColumns.filter(c => !keyColumns.includes(c));
    const availableExcludeColumns = sharedColumns.filter(c => !keyColumns.includes(c));

    useEffect(() => { setDiffColFilter(null); }, [results]);

    useEffect(() => {
        const init = async () => {
            try {
                const [configRes, parserRes] = await Promise.all([
                    fetchJson('/config/comparison'),
                    fetchJson('/config/parser'),
                ]);

                if (configRes.ok && configRes.data) {
                    const cfg = configRes.data;
                    setKeyColumns(cfg.key_columns || []);
                    setCompareColumns(cfg.compare_columns || []);
                    setExcludeColumns(cfg.exclude_columns || []);
                    setTolerances(cfg.tolerances || {});
                    setDefaultTolerance(cfg.default_tolerance != null ? String(cfg.default_tolerance) : '');
                    setLabel1(cfg.label_1 || 'Dataset 1');
                    setLabel2(cfg.label_2 || 'Dataset 2');
                    setMaxDiffRows(cfg.max_diff_rows || 500);
                    setDataset2Path(cfg.dataset2_path || '');
                    setDataset2FieldNames(cfg.dataset2_field_names || []);
                }

                if (parserRes.ok && parserRes.data) {
                    setPrimaryFilePath(parserRes.data.inputPath || '');
                }
            } catch (err) {
                setMsg({ text: `Failed to load config: ${err.message}`, type: 'error' });
            }
        };

        // Load primary dataset columns from data preview
        const loadPrimaryColumns = async () => {
            try {
                const res = await fetchJson('/data?nrows=0');
                if (res.ok && res.data && res.data.data) {
                    setDataset1Columns(Object.keys(res.data.data));
                }
            } catch { /* no primary dataset loaded yet */ }
        };

        init();
        loadPrimaryColumns();
    }, []);

    const handleUpload = async () => {
        if (!compareFile) return;
        setIsUploading(true);
        setMsg({ text: '', type: '' });
        try {
            const formData = new FormData();
            formData.append('file', compareFile);
            const res = await fetch('/upload?type=comparison', { method: 'POST', body: formData });
            if (res.status === 413) {
                setMsg({ text: 'File is too large. The server limit is 16 MB. Consider splitting or pre-processing the file before uploading.', type: 'error' });
                return;
            }
            const data = await res.json();
            if (res.ok) {
                setMsg({ text: `Uploaded: ${compareFile.name}`, type: 'success' });
                // Refresh comparison config to get updated dataset2_path + field names
                const cfgRes = await fetchJson('/config/comparison');
                if (cfgRes.ok && cfgRes.data) {
                    setDataset2Path(cfgRes.data.dataset2_path || '');
                    setDataset2FieldNames(cfgRes.data.dataset2_field_names || []);
                }
            } else {
                setMsg({ text: data.message || 'Upload failed.', type: 'error' });
            }
        } catch (err) {
            setMsg({ text: `Upload error: ${err.message}`, type: 'error' });
        } finally {
            setIsUploading(false);
        }
    };

    const handleRun = async () => {
        if (keyColumns.length === 0) {
            setMsg({ text: 'Select at least one key column before running.', type: 'error' });
            return;
        }
        setIsRunning(true);
        setMsg({ text: '', type: '' });
        setResults(null);
        try {
            // Save config first
            const parsedTol = defaultTolerance === '' ? null : Number(defaultTolerance);
            await fetch('/config/comparison', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    key_columns: keyColumns,
                    compare_columns: compareColumns,
                    exclude_columns: excludeColumns,
                    tolerances,
                    default_tolerance: isNaN(parsedTol) ? null : parsedTol,
                    label_1: label1,
                    label_2: label2,
                    max_diff_rows: maxDiffRows,
                }),
            });

            const res = await fetchJson('/compare', { method: 'POST' });
            if (res.ok && res.data && res.data.data) {
                setResults(res.data.data);
                setMsg({ text: 'Comparison complete.', type: 'success' });
            } else {
                setMsg({ text: res.data?.message || 'Comparison failed.', type: 'error' });
            }
        } catch (err) {
            setMsg({ text: `Error: ${err.message}`, type: 'error' });
        } finally {
            setIsRunning(false);
        }
    };

    const exportDiffs = () => {
        if (!results || !results.value_diffs || results.value_diffs.length === 0) return;
        const keyKeys = Object.keys(results.value_diffs[0]?.key_vals || {});
        const headers = [...keyKeys, 'column', `${label1} value`, `${label2} value`];
        const rows = results.value_diffs.map(d => [
            ...keyKeys.map(k => d.key_vals[k]),
            d.column,
            d.value_1,
            d.value_2,
        ]);
        exportToCsv('comparison_diffs', headers, rows);
    };

    const exportToMarkdown = () => {
        if (!results) return;
        const mdTable = (headers, rows) => {
            const sep = headers.map(() => '---').join(' | ');
            return [
                '| ' + headers.join(' | ') + ' |',
                '| ' + sep + ' |',
                ...rows.map(r => '| ' + r.map(v => String(v ?? '—').replace(/\|/g, '\\|')).join(' | ') + ' |'),
            ].join('\n');
        };

        const lines = [];
        lines.push(`# Dataset Comparison Report`);
        lines.push(`\n**${label1}** vs **${label2}**  `);
        lines.push(`Generated: ${new Date().toLocaleString()}\n`);

        // Schema
        lines.push(`## Schema Comparison\n`);
        lines.push(`### Shared Columns (${results.schema.shared_columns.length})\n`);
        if (results.schema.shared_columns.length)
            lines.push(mdTable(['Column'], results.schema.shared_columns.map(c => [c])));
        else lines.push('_None_');

        lines.push(`\n### Only in ${label1} (${results.schema.only_in_1.length})\n`);
        if (results.schema.only_in_1.length)
            lines.push(mdTable(['Column'], results.schema.only_in_1.map(c => [c])));
        else lines.push('_None_');

        lines.push(`\n### Only in ${label2} (${results.schema.only_in_2.length})\n`);
        if (results.schema.only_in_2.length)
            lines.push(mdTable(['Column'], results.schema.only_in_2.map(c => [c])));
        else lines.push('_None_');

        const mismatches = results.schema.dtype_comparison.filter(r => !r.match);
        if (mismatches.length) {
            lines.push(`\n### Data Type Mismatches\n`);
            lines.push(mdTable(['Column', label1, label2], mismatches.map(r => [r.column, r.dtype_1, r.dtype_2])));
        }

        // Coverage
        lines.push(`\n## Row Coverage\n`);
        lines.push(mdTable(['Metric', 'Count'], [
            [`${label1} rows`, results.coverage.rows_in_1.toLocaleString()],
            [`${label2} rows`, results.coverage.rows_in_2.toLocaleString()],
            ['**Matched rows**', `**${results.coverage.matched.toLocaleString()}**`],
            [`Only in ${label1}`, results.coverage.only_in_1.toLocaleString()],
            [`Only in ${label2}`, results.coverage.only_in_2.toLocaleString()],
            ['Union total', results.coverage.union_total.toLocaleString()],
            ['Key match %', `${(results.coverage.match_pct * 100).toFixed(1)}%`],
            [`Duplicate keys in ${label1}`, results.coverage.duplicate_keys_1.toLocaleString()],
            [`Duplicate keys in ${label2}`, results.coverage.duplicate_keys_2.toLocaleString()],
        ]));

        // Value summary
        if (results.summary.column_summary?.length) {
            lines.push(`\n## Value Comparison Summary\n`);
            lines.push(`Matched rows: **${results.summary.matched_rows.toLocaleString()}** | Rows with diffs: **${results.summary.rows_with_diffs.toLocaleString()}** | Overall match: **${results.summary.overall_match_pct}%**\n`);
            lines.push(mdTable(
                ['Column', 'Tolerance', 'Matched rows', 'Diffs', '% Match'],
                results.summary.column_summary.map(r => [
                    r.column,
                    r.tolerance != null ? String(r.tolerance) : '—',
                    r.matched_rows.toLocaleString(),
                    r.n_diffs.toLocaleString(),
                    `${r.pct_match}%`,
                ]),
            ));
        }

        // Detailed diffs
        lines.push(`\n## Detailed Differences\n`);
        if (!results.value_diffs.length) {
            lines.push('_No differences found in matched rows._');
        } else {
            const activeDiffs = diffColFilter
                ? results.value_diffs.filter(d => diffColFilter.has(d.column))
                : results.value_diffs;
            if (diffColFilter)
                lines.push(`_Filtered to: ${[...diffColFilter].join(', ')}_\n`);
            const keyKeys = Object.keys(activeDiffs[0]?.key_vals || {});
            lines.push(mdTable(
                [...keyKeys, 'Column', label1, label2],
                activeDiffs.map(d => [
                    ...keyKeys.map(k => d.key_vals[k]),
                    d.column,
                    d.value_1,
                    d.value_2,
                ]),
            ));
        }

        const blob = new Blob([lines.join('\n')], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'comparison_report.md';
        a.click();
        URL.revokeObjectURL(url);
    };

    // --- Chart builders ---
    const buildCoverageChart = (cov) => ({
        chart: { type: 'column', height: 260 },
        title: { text: null },
        xAxis: { categories: ['Matched', `Only in ${label1}`, `Only in ${label2}`], labels: { style: { fontFamily: '"Courier New", Courier, monospace', fontSize: '11px' } } },
        yAxis: { title: { text: 'Rows' } },
        legend: { enabled: false },
        series: [{ name: 'Rows', data: [cov.matched, cov.only_in_1, cov.only_in_2], color: '#4477aa' }],
        credits: { enabled: false },
    });

    const buildMatchPctChart = (colSummary) => ({
        chart: { type: 'bar', height: Math.max(200, colSummary.length * 28 + 80) },
        title: { text: null },
        xAxis: { categories: colSummary.map(r => r.column), labels: { style: { fontFamily: '"Courier New", Courier, monospace', fontSize: '11px' } } },
        yAxis: { title: { text: '% Match' }, max: 100, min: 0 },
        legend: { enabled: false },
        series: [{ name: '% Match', data: colSummary.map(r => r.pct_match), color: '#44aa77' }],
        credits: { enabled: false },
    });

    return (
        <div className="config-form-container">
            <h2>Compare Datasets</h2>

            {/* Active dataset indicator */}
            <div className="section" style={{ marginBottom: '1rem' }}>
                <strong>Active dataset (Dataset 1):</strong>{' '}
                <code style={{ fontFamily: '"Courier New", Courier, monospace', fontSize: '0.9em' }}>
                    {primaryFilePath || <em style={{ color: '#888' }}>No file loaded — upload a primary dataset via the Upload tab first.</em>}
                </code>
            </div>

            {/* Step 1: Upload comparison file */}
            <div className="section" style={{ marginBottom: '1.5rem' }}>
                <h3>Step 1: Upload Comparison File (Dataset 2)</h3>
                <div className="flex-between" style={{ gap: '8px', alignItems: 'center' }}>
                    <input
                        type="file"
                        accept=".csv"
                        onChange={e => setCompareFile(e.target.files[0] || null)}
                        style={{ flex: 1 }}
                    />
                    <button onClick={handleUpload} disabled={!compareFile || isUploading}>
                        {isUploading ? 'Uploading…' : 'Upload'}
                    </button>
                </div>
                {dataset2Path && (
                    <div style={{ marginTop: '6px', color: '#555', fontSize: '0.85em' }}>
                        Current: <code>{dataset2Path}</code>
                        {dataset2FieldNames.length > 0 && ` (${dataset2FieldNames.length} columns)`}
                    </div>
                )}
            </div>

            {/* Step 2: Key columns */}
            <div className="section" style={{ marginBottom: '1.5rem' }}>
                <h3>Step 2: Key Columns</h3>
                <p style={{ fontSize: '0.85em', color: '#666', margin: '0 0 8px' }}>
                    Columns used to match rows between datasets. Must exist in both files.
                </p>
                <MultiSelect
                    options={availableKeyColumns}
                    selected={keyColumns}
                    onChange={setKeyColumns}
                    emptyMessage="No key columns selected."
                    onSelectAll={() => setKeyColumns(availableKeyColumns)}
                />
            </div>

            {/* Step 3: Value columns & tolerances */}
            <div className="section" style={{ marginBottom: '1.5rem' }}>
                <h3>Step 3: Configure Values (optional)</h3>
                <div className="responsive-grid">
                    <div>
                        <label><strong>Compare Columns</strong> <span style={{ color: '#888', fontSize: '0.85em' }}>(empty = all shared)</span></label>
                        <MultiSelect
                            options={availableCompareColumns}
                            selected={compareColumns}
                            onChange={setCompareColumns}
                            emptyMessage="All shared columns will be compared."
                            onSelectAll={() => setCompareColumns(availableCompareColumns)}
                        />
                    </div>
                    <div>
                        <label><strong>Exclude Columns</strong></label>
                        <MultiSelect
                            options={availableExcludeColumns}
                            selected={excludeColumns}
                            onChange={setExcludeColumns}
                            emptyMessage="No columns excluded."
                        />
                    </div>
                </div>

                <div style={{ marginTop: '1rem' }}>
                    <label><strong>Per-Column Tolerances</strong> <span style={{ color: '#888', fontSize: '0.85em' }}>(column → value; use a number, "contains", or timedelta like "1h")</span></label>
                    <DataEditor data={tolerances} keyOptions={sharedColumns} onChange={setTolerances} />
                </div>

                <div className="responsive-grid" style={{ marginTop: '0.5rem', gridTemplateColumns: 'repeat(4, 1fr)' }}>
                    <div>
                        <label><strong>Default Tolerance</strong> <span style={{ color: '#888', fontSize: '0.85em' }}>(applied to all unlisted columns; empty = exact match)</span></label>
                        <input
                            type="number"
                            step="any"
                            value={defaultTolerance}
                            onChange={e => setDefaultTolerance(e.target.value)}
                            placeholder="exact match"
                            style={{ width: '120px', fontFamily: '"Courier New", Courier, monospace' }}
                        />
                    </div>
                    <div>
                        <label><strong>Max Diff Rows</strong></label>
                        <input
                            type="number"
                            min="1"
                            value={maxDiffRows}
                            onChange={e => setMaxDiffRows(Number(e.target.value))}
                            style={{ width: '100px', fontFamily: '"Courier New", Courier, monospace' }}
                        />
                    </div>
                    <div>
                        <label><strong>Label for Dataset 1</strong></label>
                        <input
                            type="text"
                            value={label1}
                            onChange={e => setLabel1(e.target.value)}
                            style={{ width: '160px', fontFamily: '"Courier New", Courier, monospace' }}
                        />
                    </div>
                    <div>
                        <label><strong>Label for Dataset 2</strong></label>
                        <input
                            type="text"
                            value={label2}
                            onChange={e => setLabel2(e.target.value)}
                            style={{ width: '160px', fontFamily: '"Courier New", Courier, monospace' }}
                        />
                    </div>
                </div>
            </div>

            {/* Run button */}
            <div style={{ marginBottom: '1rem' }}>
                <button
                    onClick={handleRun}
                    disabled={isRunning || keyColumns.length === 0}
                    style={{ fontSize: '1rem', padding: '6px 18px' }}
                >
                    {isRunning ? 'Running…' : 'Run Comparison'}
                </button>
                {keyColumns.length === 0 && (
                    <span style={{ marginLeft: '12px', color: '#888', fontSize: '0.85em' }}>Select key columns to enable.</span>
                )}
            </div>

            {/* Status message */}
            {msg.text && (
                <div className={`status-message ${msg.type}`} style={{ marginBottom: '1rem' }}>
                    {msg.text}
                </div>
            )}

            {/* --- Results --- */}
            {results && (
                <>
                    {/* Schema */}
                    <div className="section" style={{ marginBottom: '1.5rem' }}>
                        <h3>Schema Comparison</h3>
                        <div className="responsive-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)' }}>
                            <div>
                                <h4>Shared Columns ({results.schema.shared_columns.length})</h4>
                                <div className="table-container">
                                    <table>
                                        <tbody>
                                            {results.schema.shared_columns.map(c => <tr key={c}><td>{c}</td></tr>)}
                                            {results.schema.shared_columns.length === 0 && <tr><td style={{ color: '#888' }}>None</td></tr>}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div>
                                <h4>Only in {label1} ({results.schema.only_in_1.length})</h4>
                                <div className="table-container">
                                    <table>
                                        <tbody>
                                            {results.schema.only_in_1.map(c => <tr key={c}><td>{c}</td></tr>)}
                                            {results.schema.only_in_1.length === 0 && <tr><td style={{ color: '#888' }}>None</td></tr>}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            <div>
                                <h4>Only in {label2} ({results.schema.only_in_2.length})</h4>
                                <div className="table-container">
                                    <table>
                                        <tbody>
                                            {results.schema.only_in_2.map(c => <tr key={c}><td>{c}</td></tr>)}
                                            {results.schema.only_in_2.length === 0 && <tr><td style={{ color: '#888' }}>None</td></tr>}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>

                        {results.schema.dtype_comparison.some(r => !r.match) && (
                            <div style={{ marginTop: '1rem' }}>
                                <h4>Data Type Mismatches</h4>
                                <div className="table-container">
                                    <table>
                                        <thead>
                                            <tr><th>Column</th><th>{label1}</th><th>{label2}</th></tr>
                                        </thead>
                                        <tbody>
                                            {results.schema.dtype_comparison.filter(r => !r.match).map(r => (
                                                <tr key={r.column}>
                                                    <td>{r.column}</td>
                                                    <td><code>{r.dtype_1}</code></td>
                                                    <td><code>{r.dtype_2}</code></td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Coverage */}
                    <div className="section" style={{ marginBottom: '1.5rem' }}>
                        <h3>Row Coverage</h3>
                        <div className="responsive-grid">
                            <div>
                                <table>
                                    <tbody>
                                        <tr><td>{label1} rows</td><td><strong>{results.coverage.rows_in_1.toLocaleString()}</strong></td></tr>
                                        <tr><td>{label2} rows</td><td><strong>{results.coverage.rows_in_2.toLocaleString()}</strong></td></tr>
                                        <tr style={{ backgroundColor: '#fffbcc' }}><td>Matched rows</td><td><strong>{results.coverage.matched.toLocaleString()}</strong></td></tr>
                                        <tr><td>Only in {label1}</td><td><strong>{results.coverage.only_in_1.toLocaleString()}</strong></td></tr>
                                        <tr><td>Only in {label2}</td><td><strong>{results.coverage.only_in_2.toLocaleString()}</strong></td></tr>
                                        <tr><td>Union total</td><td><strong>{results.coverage.union_total.toLocaleString()}</strong></td></tr>
                                        <tr><td>Key match %</td><td><strong>{(results.coverage.match_pct * 100).toFixed(1)}%</strong></td></tr>
                                        <tr><td>Duplicate keys in {label1}</td><td>{results.coverage.duplicate_keys_1.toLocaleString()}</td></tr>
                                        <tr><td>Duplicate keys in {label2}</td><td>{results.coverage.duplicate_keys_2.toLocaleString()}</td></tr>
                                    </tbody>
                                </table>
                            </div>
                            <div>
                                <HighchartsReact
                                    highcharts={Highcharts}
                                    options={buildCoverageChart(results.coverage)}
                                />
                            </div>
                        </div>

                        {results.coverage.key_stats && results.coverage.key_stats.length > 0 && (
                            <div style={{ marginTop: '1rem' }}>
                                <h4>Key Column Stats</h4>
                                <div className="table-container">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>Key Column</th>
                                                <th>Unique in {label1}</th>
                                                <th>Total in {label1}</th>
                                                <th>Unique in {label2}</th>
                                                <th>Total in {label2}</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {results.coverage.key_stats.map(r => (
                                                <tr key={r.key_column}>
                                                    <td>{r.key_column}</td>
                                                    <td>{r.unique_1?.toLocaleString()}</td>
                                                    <td>{r.total_1?.toLocaleString()}</td>
                                                    <td>{r.unique_2?.toLocaleString()}</td>
                                                    <td>{r.total_2?.toLocaleString()}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Column match summary */}
                    {results.summary.column_summary && results.summary.column_summary.length > 0 && (
                        <div className="section" style={{ marginBottom: '1.5rem' }}>
                            <h3>Value Comparison Summary</h3>
                            <p>
                                Matched rows: <strong>{results.summary.matched_rows.toLocaleString()}</strong> &nbsp;|&nbsp;
                                Rows with diffs: <strong>{results.summary.rows_with_diffs.toLocaleString()}</strong> &nbsp;|&nbsp;
                                Overall match: <strong>{results.summary.overall_match_pct}%</strong>
                            </p>
                            <div className="responsive-grid">
                                <div>
                                    <div className="table-container">
                                        <table>
                                            <thead>
                                                <tr>
                                                    <th>Column</th>
                                                    <th>Tolerance</th>
                                                    <th>Matched rows</th>
                                                    <th>Diffs</th>
                                                    <th>% Match</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {results.summary.column_summary.map(r => (
                                                    <tr key={r.column}>
                                                        <td>{r.column}</td>
                                                        <td><code>{r.tolerance != null ? String(r.tolerance) : '—'}</code></td>
                                                        <td>{r.matched_rows.toLocaleString()}</td>
                                                        <td>{r.n_diffs.toLocaleString()}</td>
                                                        <td>{r.pct_match}%</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                                <div>
                                    <HighchartsReact
                                        highcharts={Highcharts}
                                        options={buildMatchPctChart(results.summary.column_summary)}
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Detailed diffs */}
                    <div className="section" style={{ marginBottom: '1.5rem' }}>
                        <h3>
                            Detailed Differences
                            {results.value_diffs.length > 0 && (
                                <button
                                    onClick={exportDiffs}
                                    style={{ marginLeft: '12px', fontSize: '0.85em', padding: '2px 10px' }}
                                >
                                    Export CSV
                                </button>
                            )}
                            <button
                                onClick={exportToMarkdown}
                                style={{ marginLeft: '8px', fontSize: '0.85em', padding: '2px 10px' }}
                            >
                                Export Markdown
                            </button>
                        </h3>
                        {results.value_diffs.length === 0 ? (
                            <p style={{ color: '#555' }}>No differences found in matched rows.</p>
                        ) : (() => {
                            const distinctCols = [...new Set(results.value_diffs.map(d => d.column))];
                            const timeKey = Object.keys(results.value_diffs[0]?.key_vals || {})
                                .find(k => /time|date/i.test(k));
                            const sorted = timeKey
                                ? [...results.value_diffs].sort((a, b) => {
                                    const ta = new Date(a.key_vals[timeKey]);
                                    const tb = new Date(b.key_vals[timeKey]);
                                    if (isNaN(ta)) return 1;
                                    if (isNaN(tb)) return -1;
                                    return ta - tb;
                                })
                                : results.value_diffs;
                            const filtered = diffColFilter
                                ? sorted.filter(d => diffColFilter.has(d.column))
                                : sorted;
                            const toggleCol = (col) => {
                                setDiffColFilter(prev => {
                                    const next = new Set(prev ?? distinctCols);
                                    next.has(col) ? next.delete(col) : next.add(col);
                                    return next.size === distinctCols.length ? null : next;
                                });
                            };
                            return (
                                <>
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '8px', alignItems: 'center' }}>
                                        <span style={{ fontSize: '0.85em', color: '#666' }}>Show:</span>
                                        {distinctCols.map(col => {
                                            const active = !diffColFilter || diffColFilter.has(col);
                                            return (
                                                <button
                                                    key={col}
                                                    onClick={() => toggleCol(col)}
                                                    style={{
                                                        fontSize: '0.8em',
                                                        padding: '2px 8px',
                                                        borderRadius: '12px',
                                                        border: '1px solid #aaa',
                                                        cursor: 'pointer',
                                                        background: active ? '#4477aa' : '#eee',
                                                        color: active ? '#fff' : '#555',
                                                    }}
                                                >
                                                    {col}
                                                </button>
                                            );
                                        })}
                                        {diffColFilter && (
                                            <button
                                                onClick={() => setDiffColFilter(null)}
                                                style={{ fontSize: '0.8em', padding: '2px 8px', cursor: 'pointer' }}
                                            >
                                                All
                                            </button>
                                        )}
                                    </div>
                                    <div className="table-container">
                                        <table>
                                            <thead>
                                                <tr>
                                                    {Object.keys(results.value_diffs[0]?.key_vals || {}).map(k => (
                                                        <th key={k}>{k}{k === timeKey ? ' ↑' : ''}</th>
                                                    ))}
                                                    <th>Column</th>
                                                    <th>{label1}</th>
                                                    <th>{label2}</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {filtered.map((d, i) => (
                                                    <tr key={i}>
                                                        {Object.values(d.key_vals).map((v, j) => (
                                                            <td key={j}>{String(v)}</td>
                                                        ))}
                                                        <td><code>{d.column}</code></td>
                                                        <td style={{ backgroundColor: '#fde8e8' }}>{d.value_1 != null ? String(d.value_1) : '—'}</td>
                                                        <td style={{ backgroundColor: '#e8f0fd' }}>{d.value_2 != null ? String(d.value_2) : '—'}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </>
                            );
                        })()}
                        {results.value_diffs.length >= maxDiffRows && (
                            <p style={{ color: '#888', fontSize: '0.85em', marginTop: '6px' }}>
                                Showing first {maxDiffRows} diff records. Increase Max Diff Rows to see more.
                            </p>
                        )}
                    </div>
                </>
            )}
        </div>
    );
}

export default CompareDatasetPage;
