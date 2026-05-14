import React, { useState, useEffect } from 'react';
import MultiSelect from './MultiSelect';
import { fetchJson } from '../utils/fetchJson';
import { exportToCsv } from '../utils/exportToCsv';
import Highcharts from 'highcharts/highstock';
import HighchartsReact from 'highcharts-react-official';
import HC_more from 'highcharts/highcharts-more';

// Initialize Highcharts More for area range
if (typeof Highcharts === 'object') {
    if (typeof HC_more === 'function') {
        HC_more(Highcharts);
    } else if (HC_more && typeof HC_more.default === 'function') {
        HC_more.default(Highcharts);
    }
}

const ForecastPage = () => {
    const [loading, setLoading] = useState(true);
    const [msg, setMsg] = useState({ text: '', type: '' });

    // Dataset context
    const [previewData, setPreviewData] = useState(null);
    const dataColumns = previewData ? Object.keys(previewData) : [];

    // Config state
    const [targetDataColumns, setTargetDataColumns] = useState([]);
    const [dateColumn, setDateColumn] = useState('');
    const [horizon, setHorizon] = useState(10);

    // Results
    const [isForecasting, setIsForecasting] = useState(false);
    const [forecastData, setForecastData] = useState(null);

    // Evaluation
    const [isEvaluating, setIsEvaluating] = useState(false);
    const [evaluationData, setEvaluationData] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Fetch full dataset for charting inputs and configs for init
                const [configRes, dataRes] = await Promise.all([
                    fetchJson('/config/forecast'),
                    fetchJson('/data')
                ]);

                const forecastConf = configRes.data;
                const dataJson = dataRes.data;

                if (dataJson && dataJson.data) {
                    setPreviewData(dataJson.data);
                }

                if (forecastConf) {
                    setTargetDataColumns(forecastConf.target_data_columns || []);
                    setDateColumn(forecastConf.date_column || '');
                    setHorizon(forecastConf.horizon || 10);
                }
            } catch (err) {
                setMsg({ text: `Failed to load data: ${err.message}`, type: 'error' });
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const handleForecast = async () => {
        if (!dateColumn) {
            setMsg({ text: 'Please select a date column.', type: 'error' });
            return;
        }
        if (targetDataColumns.length === 0) {
            setMsg({ text: 'Please select at least one target column.', type: 'error' });
            return;
        }

        setIsForecasting(true);
        setForecastData(null);
        setMsg({ text: 'Saving config and generating forecast...', type: 'info' });

        try {
            // Update configuration
            const outgoingConfig = {
                target_data_columns: targetDataColumns,
                date_column: dateColumn,
                horizon: Number(horizon)
            };

            const configRes = await fetch('/config/forecast', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(outgoingConfig)
            });
            if (!configRes.ok) throw new Error('Config update failed');

            // Generate forecast
            const forecastRes = await fetch('/forecast?operation=generate', { cache: 'no-store' });
            if (!forecastRes.ok) throw new Error('Forecast generation failed');

            const forecastJson = await forecastRes.json();
            if (forecastJson.data) {
                setForecastData(forecastJson.data);
                setMsg({ text: 'Forecast generated successfully.', type: 'success' });
            } else {
                setMsg({ text: 'No data returned from forecast.', type: 'error' });
            }
        } catch (err) {
            setMsg({ text: `Error: ${err.message}`, type: 'error' });
        } finally {
            setIsForecasting(false);
        }
    };

    const handleEvaluate = async () => {
        if (!dateColumn) {
            setMsg({ text: 'Please select a date column before evaluating.', type: 'error' });
            return;
        }
        if (targetDataColumns.length === 0) {
            setMsg({ text: 'Please select at least one target column before evaluating.', type: 'error' });
            return;
        }

        setIsEvaluating(true);
        setEvaluationData(null);
        setMsg({ text: 'Evaluating forecast — this may take a moment...', type: 'info' });

        try {
            // Persist the current config first so the backend uses the right columns
            const outgoingConfig = {
                target_data_columns: targetDataColumns,
                date_column: dateColumn,
                horizon: Number(horizon)
            };
            const configRes = await fetch('/config/forecast', {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(outgoingConfig)
            });
            if (!configRes.ok) throw new Error('Config update failed');

            const evalRes = await fetch('/forecast?operation=evaluate', { cache: 'no-store' });
            if (!evalRes.ok) throw new Error('Forecast evaluation failed');

            const evalJson = await evalRes.json();
            if (evalJson.data) {
                setEvaluationData(evalJson.data);
                setMsg({ text: 'Evaluation complete.', type: 'success' });
            } else {
                setMsg({ text: 'No evaluation data returned.', type: 'error' });
            }
        } catch (err) {
            setMsg({ text: `Error: ${err.message}`, type: 'error' });
        } finally {
            setIsEvaluating(false);
        }
    };

    // ─── Chart Data Processing ────────────────────────────────────────────────
    let chartOptions = {};

    if (previewData && dateColumn) {
        const buildSeriesData = () => {
            const seriesList = [];
            const timesKeys = Object.keys(previewData[dateColumn] || {});

            const parseDate = (dStr) => {
                const ts = new Date(dStr).getTime();
                return isNaN(ts) ? null : ts;
            };

            // Format input historical data
            targetDataColumns.forEach((colName) => {
                if (previewData[colName]) {
                    const dataPoints = [];
                    timesKeys.forEach(idx => {
                        const dateStr = String(previewData[dateColumn][idx]);
                        const val = Number(previewData[colName][idx]);
                        const ts = parseDate(dateStr);
                        if (!isNaN(val) && ts !== null) {
                            dataPoints.push([ts, val]);
                        }
                    });

                    dataPoints.sort((a, b) => a[0] - b[0]);

                    seriesList.push({
                        name: `${colName} (Historical)`,
                        type: 'line',
                        data: dataPoints,
                        lineWidth: 2,
                        color: '#7cb5ec' // Default highcharts blue for historical
                    });
                }
            });

            // Format Generated Forecast data 
            if (forecastData && forecastData.series) {
                const fKeys = Object.keys(forecastData.series);

                targetDataColumns.forEach(colName => {
                    const pointData = [];
                    const range80Data = [];
                    const range90Data = [];

                    fKeys.forEach(idx => {
                        if (forecastData.series[idx] === colName) {
                            // Highcharts stock needs exact timestamps
                            const fDate = String(forecastData[dateColumn]?.[idx]);
                            const ts = parseDate(fDate);

                            if (ts !== null) {
                                pointData.push([ts, forecastData.median[idx]]);
                                range80Data.push([ts, forecastData.lower_80[idx], forecastData.upper_80[idx]]);
                                range90Data.push([ts, forecastData.lower_90[idx], forecastData.upper_90[idx]]);
                            }
                        }
                    });

                    // Forecast points sorted by time
                    pointData.sort((a, b) => a[0] - b[0]);
                    range80Data.sort((a, b) => a[0] - b[0]);
                    range90Data.sort((a, b) => a[0] - b[0]);

                    if (pointData.length > 0) {
                        seriesList.push({
                            name: `${colName} (10% - 90% Interval)`,
                            type: 'arearange',
                            data: range90Data,
                            lineWidth: 0,
                            color: '#ff9800', // Orange forecast color 
                            fillOpacity: 0.15,
                            zIndex: 0
                        });

                        seriesList.push({
                            name: `${colName} (20% - 80% Interval)`,
                            type: 'arearange',
                            data: range80Data,
                            lineWidth: 0,
                            color: '#ff9800',
                            fillOpacity: 0.35,
                            zIndex: 0
                        });

                        seriesList.push({
                            name: `${colName} (Median Predicted)`,
                            type: 'line',
                            data: pointData,
                            lineWidth: 2,
                            dashStyle: 'ShortDash',
                            color: '#ff9800',
                            zIndex: 1
                        });
                    }
                });
            }

            return seriesList;
        };

        chartOptions = {
            title: {
                text: 'Historical Data and Forecast'
            },
            rangeSelector: {
                enabled: true
            },
            xAxis: {
                type: 'datetime',
                title: { text: dateColumn },
            },
            yAxis: {
                title: { text: 'Value' }
            },
            tooltip: {
                shared: true,
                crosshairs: true
            },
            plotOptions: {
                line: { marker: { enabled: false } },
                arearange: { marker: { enabled: false } }
            },
            series: buildSeriesData()
        };
    }

    if (loading) return <div>Loading...</div>;

    return (
        <div className="clean-page">
            <h2>Time Series Forecasting</h2>

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
                                {Object.keys(previewData[Object.keys(previewData)[0]] || {}).slice(0, 10).map((rowIndex) => (
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
                <h3>Parameters</h3>
                <p style={{ marginBottom: '1rem' }}>
                    Select the historical time/date column, the value columns to model, and how far into the future the forecast should look.
                </p>

                <div className="responsive-grid grid-2-col">
                    <div className="form-group">
                        <label>Date/Time Column</label>
                        <select
                            value={dateColumn}
                            onChange={e => setDateColumn(e.target.value)}
                        >
                            <option value="">-- Select --</option>
                            {dataColumns.map(c => <option key={c} value={c}>{c}</option>)}
                        </select>
                    </div>

                    <div className="form-group">
                        <label>Forecast Horizon (Steps)</label>
                        <input
                            type="number"
                            min="1"
                            value={horizon}
                            onChange={e => setHorizon(e.target.value)}
                        />
                    </div>
                </div>

                <div className="form-group">
                    <label>Values to Forecast</label>
                    <MultiSelect
                        options={dataColumns}
                        selected={targetDataColumns}
                        onChange={setTargetDataColumns}
                        onSelectAll={() => setTargetDataColumns([...dataColumns])}
                        emptyMessage="No columns selected."
                    />
                </div>

                <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                    <button className="primary" onClick={handleForecast} disabled={isForecasting || isEvaluating}>
                        {isForecasting ? 'Running Model...' : 'Generate Forecast'}
                    </button>
                    <button className="secondary" onClick={handleEvaluate} disabled={isForecasting || isEvaluating}>
                        {isEvaluating ? 'Evaluating...' : 'Evaluate Forecast'}
                    </button>
                </div>
            </div>

            <div className="section" style={{ height: '550px' }}>
                <h3>Forecast Results</h3>
                {dateColumn ? (
                    <HighchartsReact
                        highcharts={Highcharts}
                        constructorType={'stockChart'}
                        options={chartOptions}
                    />
                ) : (
                    <p style={{ color: '#666' }}>Please configure and select a date column to render the chart.</p>
                )}
            </div>

            {evaluationData && (() => {
                const parseDate = (dStr) => {
                    if (!dStr) return null;
                    const ts = new Date(dStr).getTime();
                    return isNaN(ts) ? null : ts;
                };

                const dates = evaluationData[dateColumn] || {};

                return targetDataColumns.map(targetCol => {
                    const forecasts = evaluationData[`${targetCol}_forecast`] || {};
                    const errors = evaluationData[`${targetCol}_error`] || {};
                    const actuals = evaluationData[targetCol] || {};

                    const actualData = [];
                    const forecastData = [];
                    const errorData = [];

                    const keys = Object.keys(dates);

                    keys.forEach(idx => {
                        const ts = parseDate(String(dates[idx]));
                        if (ts === null) return;

                        const actual = actuals[idx];
                        const forecast = forecasts[idx];
                        const err = errors[idx];

                        if (actual != null) actualData.push([ts, actual]);
                        if (forecast != null) forecastData.push([ts, forecast]);
                        if (err != null) errorData.push([ts, err]);
                    });

                    const sort = arr => [...arr].sort((a, b) => a[0] - b[0]);

                    const evalSeries = [];
                    if (targetCol) {
                        evalSeries.push({
                            name: `${targetCol} — Predicted`,
                            type: 'line',
                            data: sort(forecastData),
                            lineWidth: 2,
                            dashStyle: 'ShortDash',
                            color: '#ff9800',
                            zIndex: 1,
                            yAxis: 0
                        });
                        evalSeries.push({
                            name: `${targetCol} — Actual`,
                            type: 'line',
                            data: sort(actualData),
                            lineWidth: 2,
                            color: '#7cb5ec',
                            zIndex: 2,
                            yAxis: 0
                        });
                        evalSeries.push({
                            name: `${targetCol} — Residual Error`,
                            type: 'column',
                            data: sort(errorData),
                            color: '#ef5350',
                            opacity: 0.6,
                            zIndex: 1,
                            yAxis: 1
                        });
                    }

                    const evalChartOptions = {
                        title: { text: `Forecast Evaluation — ${targetCol}` },
                        rangeSelector: { enabled: true },
                        xAxis: { type: 'datetime', title: { text: dateColumn } },
                        yAxis: [
                            { title: { text: 'Value' }, height: '65%' },
                            { title: { text: 'Residual Error' }, top: '70%', height: '30%', offset: 0, opposite: false }
                        ],
                        tooltip: { shared: true, crosshairs: true },
                        plotOptions: {
                            line: { marker: { enabled: false } },
                            arearange: { marker: { enabled: false } },
                            column: { groupPadding: 0, pointPadding: 0, borderWidth: 0 }
                        },
                        series: evalSeries
                    };

                    const meta = (evaluationData.metadata || {})[targetCol] || {};

                    const metaFields = [
                        { label: 'Mean Error Percentage', key: 'mean_absolute_percentage_error', format: v => `${Number(v).toFixed(2)}%` },
                        { label: 'Forecast Length', key: 'forecast_length', format: v => `${v} steps` },
                        { label: 'Start Date', key: 'forecast_start_date', format: v => v },
                        { label: 'End Date', key: 'forecast_end_date', format: v => v },
                        { label: 'Timespan', key: 'forecast_timespan', format: v => v },
                        { label: 'Input Records', key: 'total_input_records', format: v => Number(v).toLocaleString() },
                        { label: 'Best Variance', key: 'best_prediction_error', format: v => `${Number(v).toFixed(4)}%` },
                        { label: 'Worst Variance', key: 'worst_prediction_error', format: v => `${Number(v).toFixed(2)}%` },
                        { label: 'Best Date', key: 'best_prediction_date', format: v => v },
                        { label: 'Worst Date', key: 'worst_prediction_date', format: v => v },
                    ];

                    return (
                        <div key={targetCol} className="section">
                            <h3>Evaluation Results - {targetCol}</h3>
                            <p style={{ margin: '0 0 0.75rem', color: '#888', fontSize: '0.875rem' }}>
                                The model was trained on the first half of the dataset and forecast over the second half.
                                Blue = actual observations, orange = predicted median with confidence bands, red bars = residual error.
                            </p>
                            <div style={{ display: 'flex', gap: '1.25rem', alignItems: 'flex-start' }}>
                                {/* Evaluation chart */}
                                <div style={{ flex: 1, minWidth: 0, height: '550px' }}>
                                    <HighchartsReact
                                        highcharts={Highcharts}
                                        constructorType={'stockChart'}
                                        options={evalChartOptions}
                                    />
                                </div>

                                {/* Metadata panel — right of chart */}
                                <div style={{
                                    width: '190px',
                                    flexShrink: 0,
                                    border: '1px solid #000',
                                    background: '#fff',
                                    fontFamily: '"Times New Roman", Times, serif',
                                    fontSize: '0.9em',
                                    alignSelf: 'flex-start',
                                }}>
                                    <div style={{
                                        backgroundColor: '#ccc',
                                        fontWeight: 'bold',
                                        padding: '5px',
                                        borderBottom: '1px solid #000',
                                        fontSize: '1em',
                                    }}>
                                        Metadata
                                    </div>
                                    {metaFields.map(({ label, key, format }) => {
                                        const raw = meta[key];
                                        if (raw == null) return null;
                                        const isMape = key === 'mean_absolute_percentage_error';
                                        return (
                                            <div key={key} style={{
                                                borderBottom: '1px solid #000',
                                                padding: '4px',
                                                backgroundColor: isMape ? '#dce9f5' : 'transparent',
                                            }}>
                                                <div style={{ fontWeight: 'bold', fontSize: '0.8em', color: '#444' }}>{label}</div>
                                                <div style={{
                                                    fontFamily: '"Courier New", Courier, monospace',
                                                    fontSize: '0.85em',
                                                    color: isMape ? '#1a6faf' : '#000',
                                                    fontWeight: isMape ? 'bold' : 'normal',
                                                    wordBreak: 'break-word',
                                                }}>
                                                    {format(raw)}
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        </div>
                    );
                });
            })()}

        </div>
    );
};

export default ForecastPage;
