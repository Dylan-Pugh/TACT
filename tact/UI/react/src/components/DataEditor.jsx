import React from 'react';

const DataEditor = ({ data, columns = [], onChange }) => {
    // If it's an array of objects
    if (Array.isArray(data)) {
        return (
            <div className="data-editor" style={{ marginBottom: '1rem' }}>
                <table style={{ width: '100%', marginBottom: '0.5rem' }}>
                    <thead>
                        <tr>
                            {columns.map(c => <th key={c}>{c}</th>)}
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.map((row, i) => (
                            <tr key={i}>
                                {columns.map(c => (
                                    <td key={c}>
                                        <input
                                            type="text"
                                            value={row[c] || ''}
                                            onChange={(e) => {
                                                const newData = [...data];
                                                newData[i] = { ...newData[i], [c]: e.target.value };
                                                onChange(newData);
                                            }}
                                            style={{ width: '100%', minWidth: 0, boxSizing: 'border-box' }}
                                        />
                                    </td>
                                ))}
                                <td>
                                    <button type="button" onClick={() => {
                                        const newData = data.filter((_, idx) => idx !== i);
                                        onChange(newData);
                                    }}>Remove</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <button type="button" onClick={() => {
                    const newRow = columns.reduce((acc, c) => ({ ...acc, [c]: '' }), {});
                    onChange([...data, newRow]);
                }}>Add Row</button>
            </div>
        );
    }

    // If it's a generic dictionary
    if (typeof data === 'object' && data !== null) {
        const keys = Object.keys(data);
        return (
            <div className="data-editor" style={{ marginBottom: '1rem' }}>
                <table style={{ width: '100%', marginBottom: '0.5rem' }}>
                    <thead>
                        <tr>
                            <th>Key</th>
                            <th>Value</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {keys.map((k, i) => (
                            <tr key={i}>
                                <td>
                                    {/* We use defaultValue for key to avoid losing focus while typing,
                                        but a proper editable key is tricky. 
                                        Let's keep it simple with controlled input but handle blur/change carefully. */}
                                    <input
                                        type="text"
                                        defaultValue={k}
                                        onBlur={(e) => {
                                            const newKey = e.target.value;
                                            if (newKey !== k) {
                                                const newData = { ...data };
                                                const val = newData[k];
                                                delete newData[k];
                                                newData[newKey] = val;
                                                onChange(newData);
                                            }
                                        }}
                                        style={{ width: '100%', minWidth: 0, boxSizing: 'border-box' }}
                                    />
                                </td>
                                <td>
                                    <input
                                        type="text"
                                        value={data[k] || ''}
                                        onChange={(e) => {
                                            onChange({ ...data, [k]: e.target.value });
                                        }}
                                        style={{ width: '100%', minWidth: 0, boxSizing: 'border-box' }}
                                    />
                                </td>
                                <td>
                                    <button type="button" onClick={() => {
                                        const newData = { ...data };
                                        delete newData[k];
                                        onChange(newData);
                                    }}>Remove</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                <button type="button" onClick={() => {
                    onChange({ ...data, [`new_key_${keys.length}`]: '' });
                }}>Add Item</button>
            </div>
        );
    }

    return null;
};

export default DataEditor;
