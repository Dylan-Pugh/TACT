export const exportToCsv = (filename, headers, dataRows) => {
    const escapeCsv = (val) => {
        if (val == null) return '';
        const str = String(val);
        // Escape quotes and wrap in quotes if there are commas, newlines, or quotes
        if (str.includes(',') || str.includes('"') || str.includes('\n')) {
            return `"${str.replace(/"/g, '""')}"`;
        }
        return str;
    };

    let csvContent = headers.map(escapeCsv).join(",") + "\n";
    
    dataRows.forEach(row => {
        csvContent += row.map(escapeCsv).join(",") + "\n";
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    
    // Ensure filename ends with .csv
    if (!filename.toLowerCase().endsWith('.csv')) {
        filename += '.csv';
    }
    
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};
