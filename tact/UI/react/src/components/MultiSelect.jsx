import React from 'react';

const MultiSelect = ({ options = [], selected = [], onChange, emptyMessage = "No columns selected.", onSelectAll }) => {
    // Handle adding an option
    const handleSelect = (e) => {
        const val = e.target.value;
        if (val && !selected.includes(val)) {
            onChange([...selected, val]);
        }
        // Reset the select dropdown to the default option
        e.target.value = "";
    };

    // Handle removing a single selected option
    const handleRemove = (itemToRemove) => {
        onChange(selected.filter(item => item !== itemToRemove));
    };

    // Handle clearing all selected options
    const handleClearAll = () => {
        onChange([]);
    };

    // Options available to be selected (not already selected)
    const availableOptions = options.filter(opt => !selected.includes(opt));

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', width: '100%' }}>
            {/* Selection Dropdown & Clear All Button */}
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                <select
                    onChange={handleSelect}
                    defaultValue=""
                    style={{ flex: 1, padding: '4px', border: '1px solid #999', fontFamily: '"Courier New", Courier, monospace' }}
                >
                    <option value="" disabled>Select column to add...</option>
                    {availableOptions.map(opt => (
                        <option key={opt} value={opt}>{opt}</option>
                    ))}
                </select>

                <button
                    type="button"
                    onClick={handleClearAll}
                    disabled={selected.length === 0}
                    style={{ whiteSpace: 'nowrap' }}
                >
                    Clear All
                </button>
                {onSelectAll && (
                    <button
                        type="button"
                        onClick={onSelectAll}
                        disabled={selected.length === options.length && options.length > 0}
                        style={{ whiteSpace: 'nowrap' }}
                    >
                        Select All
                    </button>
                )}
            </div>

            {/* Selected Items Feedback container */}
            <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '6px',
                minHeight: '40px',
                padding: '8px',
                border: '1px dotted #999',
                backgroundColor: '#fff'
            }}>
                {selected.length === 0 ? (
                    <span style={{ color: '#888', fontStyle: 'italic', fontSize: '0.9em' }}>
                        {emptyMessage}
                    </span>
                ) : (
                    selected.map(item => (
                        <div
                            key={item}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px',
                                backgroundColor: '#e0e0e0',
                                border: '1px solid #999',
                                padding: '2px 6px',
                                fontFamily: '"Courier New", Courier, monospace',
                                fontSize: '0.9em'
                            }}
                        >
                            <span>{item}</span>
                            <button
                                type="button"
                                onClick={() => handleRemove(item)}
                                style={{
                                    border: 'none',
                                    background: 'transparent',
                                    padding: '0 2px',
                                    cursor: 'pointer',
                                    color: '#d00',
                                    fontWeight: 'bold',
                                    marginLeft: '4px'
                                }}
                                title="Remove"
                            >
                                x
                            </button>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default MultiSelect;
