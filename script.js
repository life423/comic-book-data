function insertComicData() {
  const url = "https://raw.githubusercontent.com/life423/comic-book-data/main/spiderman_comics_data.json";
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  
  try {
    const response = UrlFetchApp.fetch(url);
    const comics = JSON.parse(response.getContentText());
    
    // DEBUG: Log the raw data to see what we're actually getting
    Logger.log(`Raw JSON contains ${comics.length} items:`);
    comics.forEach((comic, index) => {
      Logger.log(`${index + 1}: ${comic.Title || 'UNDEFINED TITLE'}`);
    });
    
    // Filter out any empty or invalid objects
    const validComics = comics.filter(comic => comic && comic.Title && comic.Title.trim() !== '');
    Logger.log(`After filtering: ${validComics.length} valid comics`);
    
    // Process and enhance the comic data
    const processedComics = validComics.map(comic => {
      const enhancedComic = {
        ...comic,
        extractedYear: extractYearFromTitle(comic.Title),
        numericValue: extractNumericValue(comic.EstValue),
        gradeRange: extractGradeRange(comic.Grade),
        series: extractSeries(comic.Title),
        issueNumber: extractIssueNumber(comic.Title)
      };
      return enhancedComic;
    });
    
    // Sort by estimated value (highest first)
    processedComics.sort((a, b) => b.numericValue - a.numericValue);
    
    // Create comprehensive headers
    const headers = [
      "Title",
      "Series", 
      "Issue #",
      "Year",
      "Grade Range",
      "Est. Value",
      "Value (High)",
      "Key Notes",
      "Event/First Appearance",
      "Creator(s)"
    ];
    
    // Prepare data rows
    const rows = processedComics.map(comic => [
      comic.Title,
      comic.series,
      comic.issueNumber,
      comic.extractedYear,
      comic.Grade,
      comic.EstValue,
      `$${comic.numericValue}`,
      comic.KeyNotes || "N/A",
      comic.Event || "N/A",
      comic.Creator || "N/A"
    ]);
    
    // Clear and populate sheet
    sheet.clear();
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    
    if (rows.length > 0) {
      sheet.getRange(2, 1, rows.length, headers.length).setValues(rows);
    }
    
    // Apply enhanced formatting
    applyEnhancedFormatting(sheet, headers.length, rows.length);
    
    // Auto-resize columns
    sheet.autoResizeColumns(1, headers.length);
    
    Logger.log(`Successfully imported ${validComics.length} comics (${comics.length} total objects in JSON)`);
    
    // Show user-friendly alert
    SpreadsheetApp.getUi().alert(
      `Import Complete`, 
      `Imported ${validComics.length} comics from ${comics.length} JSON objects.\nCheck the logs (Extensions > Apps Script > View > Logs) for details.`, 
      SpreadsheetApp.getUi().ButtonSet.OK
    );
    
  } catch (error) {
    Logger.log(`Error importing comic data: ${error.toString()}`);
    SpreadsheetApp.getUi().alert(`Error importing data: ${error.toString()}`);
  }
}

function extractYearFromTitle(title) {
  // First, try to extract from known series patterns with approximate years
  const seriesYearMap = {
    "Amazing Spider-Man": {
      // Based on publication history of Amazing Spider-Man
      startYear: 1963,
      getYear: function(issueNum) {
        if (issueNum <= 100) return 1963 + Math.floor((issueNum - 1) / 12);
        if (issueNum <= 200) return 1971 + Math.floor((issueNum - 101) / 12);
        if (issueNum <= 300) return 1979 + Math.floor((issueNum - 201) / 12);
        if (issueNum <= 400) return 1987 + Math.floor((issueNum - 301) / 12);
        return 1995 + Math.floor((issueNum - 401) / 12);
      }
    },
    "Peter Parker, The Spectacular Spider-Man": {
      startYear: 1976,
      getYear: function(issueNum) {
        return 1976 + Math.floor((issueNum - 1) / 12);
      }
    },
    "Marvel Team-Up": {
      startYear: 1972,
      getYear: function(issueNum) {
        return 1972 + Math.floor((issueNum - 1) / 12);
      }
    },
    "Marvel Tales": {
      startYear: 1964,
      getYear: function(issueNum) {
        return 1964 + Math.floor((issueNum - 1) / 12);
      }
    }
  };
  
  // Extract series and issue number
  const series = extractSeries(title);
  const issueNum = extractIssueNumber(title);
  
  if (series && issueNum && seriesYearMap[series]) {
    return seriesYearMap[series].getYear(issueNum);
  }
  
  // Fallback: look for explicit year in title
  const yearMatch = title.match(/\b(19[6-9]\d|20[0-2]\d)\b/);
  if (yearMatch) {
    return parseInt(yearMatch[1]);
  }
  
  return "Unknown";
}

function extractSeries(title) {
  // Extract the main series name from the title
  if (title.includes("Amazing Spider-Man")) return "Amazing Spider-Man";
  if (title.includes("Peter Parker, The Spectacular Spider-Man")) return "Peter Parker, The Spectacular Spider-Man";
  if (title.includes("Spectacular Spider-Man")) return "Spectacular Spider-Man";
  if (title.includes("Marvel Team-Up")) return "Marvel Team-Up";
  if (title.includes("Marvel Tales")) return "Marvel Tales";
  
  // Generic extraction for other series
  const match = title.match(/^([^#]+)/);
  return match ? match[1].trim() : "Unknown Series";
}

function extractIssueNumber(title) {
  // Extract issue number from title
  const match = title.match(/#(\d+)/);
  return match ? parseInt(match[1]) : null;
}

function extractNumericValue(estValue) {
  if (!estValue) return 0;
  
  // Extract the higher value from ranges like "$70–$200" or "$100–$250"
  const matches = estValue.match(/\$(\d+)(?:–\$(\d+))?/);
  if (matches) {
    // If there's a range, use the higher value; otherwise use the single value
    return parseInt(matches[2] || matches[1]);
  }
  
  // Fallback: extract any numeric value
  const numMatch = estValue.match(/\d+/);
  return numMatch ? parseInt(numMatch[0]) : 0;
}

function extractGradeRange(grade) {
  // Standardize grade format and extract numeric range
  if (!grade) return "N/A";
  
  const gradeMatch = grade.match(/(\d+(?:\.\d+)?)/g);
  if (gradeMatch && gradeMatch.length >= 2) {
    return `${gradeMatch[0]} - ${gradeMatch[gradeMatch.length - 1]}`;
  } else if (gradeMatch && gradeMatch.length === 1) {
    return gradeMatch[0];
  }
  
  return grade;
}

function applyEnhancedFormatting(sheet, numCols, numRows) {
  if (numRows === 0) return;
  
  // Header formatting
  const headerRange = sheet.getRange(1, 1, 1, numCols);
  headerRange
    .setFontWeight("bold")
    .setBackground("#1f4e79")
    .setFontColor("#ffffff")
    .setHorizontalAlignment("center")
    .setBorder(true, true, true, true, true, true);
  
  // Data formatting
  if (numRows > 0) {
    const dataRange = sheet.getRange(2, 1, numRows, numCols);
    dataRange.setBorder(true, true, true, true, true, true);
    
    // Alternate row coloring
    for (let i = 2; i <= numRows + 1; i++) {
      const rowRange = sheet.getRange(i, 1, 1, numCols);
      if (i % 2 === 0) {
        rowRange.setBackground("#f2f2f2");
      }
    }
    
    // Highlight top 3 most valuable comics
    const topComicsToHighlight = Math.min(3, numRows);
    if (topComicsToHighlight > 0) {
      const topRange = sheet.getRange(2, 1, topComicsToHighlight, numCols);
      topRange.setBackground("#fff2cc");
    }
    
    // Format value columns (Est. Value and Value High)
    if (numCols >= 7) {
      const valueRange1 = sheet.getRange(2, 6, numRows, 1); // Est. Value column
      const valueRange2 = sheet.getRange(2, 7, numRows, 1); // Value (High) column
      
      valueRange1.setHorizontalAlignment("right");
      valueRange2.setHorizontalAlignment("right");
      valueRange2.setNumberFormat("$#,##0");
    }
    
    // Center align issue numbers and years
    if (numCols >= 4) {
      const issueRange = sheet.getRange(2, 3, numRows, 1); // Issue # column
      const yearRange = sheet.getRange(2, 4, numRows, 1);  // Year column
      
      issueRange.setHorizontalAlignment("center");
      yearRange.setHorizontalAlignment("center");
    }
  }
  
  // Freeze header row
  sheet.setFrozenRows(1);
}

function createSummaryStats() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const lastRow = sheet.getLastRow();
  
  if (lastRow <= 1) {
    SpreadsheetApp.getUi().alert("No data found. Please import comic data first.");
    return;
  }
  
  // Create a new sheet for summary statistics
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  let summarySheet;
  
  try {
    summarySheet = spreadsheet.getSheetByName("Summary Stats");
    if (summarySheet) {
      summarySheet.clear();
    }
  } catch (e) {
    summarySheet = spreadsheet.insertSheet("Summary Stats");
  }
  
  // Calculate statistics
  const valueColumn = 7; // Value (High) column
  const seriesColumn = 2; // Series column
  const yearColumn = 4;   // Year column
  
  const valueRange = sheet.getRange(2, valueColumn, lastRow - 1, 1);
  const values = valueRange.getValues().flat().map(v => {
    if (typeof v === 'string') {
      return parseInt(v.replace(/\D/g, '')) || 0;
    }
    return v || 0;
  });
  
  const totalValue = values.reduce((sum, val) => sum + val, 0);
  const avgValue = totalValue / values.length;
  const maxValue = Math.max(...values);
  const minValue = Math.min(...values.filter(v => v > 0));
  
  // Create summary report
  const summaryData = [
    ["Comic Collection Summary", ""],
    ["", ""],
    ["Total Comics:", lastRow - 1],
    ["Total Collection Value:", `$${totalValue.toLocaleString()}`],
    ["Average Comic Value:", `$${Math.round(avgValue).toLocaleString()}`],
    ["Most Valuable Comic:", `$${maxValue.toLocaleString()}`],
    ["Least Valuable Comic:", `$${minValue.toLocaleString()}`],
    ["", ""],
    ["Generated:", new Date().toLocaleDateString()]
  ];
  
  summarySheet.getRange(1, 1, summaryData.length, 2).setValues(summaryData);
  
  // Format summary sheet
  summarySheet.getRange(1, 1).setFontSize(16).setFontWeight("bold");
  summarySheet.getRange(3, 1, 6, 1).setFontWeight("bold");
  summarySheet.autoResizeColumns(1, 2);
  
  SpreadsheetApp.getUi().alert("Summary statistics created in 'Summary Stats' sheet!");
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("Comic Collection Tools")
    .addItem("Import Comic Data", "insertComicData")
    .addItem("Create Summary Stats", "createSummaryStats")
    .addSeparator()
    .addItem("Refresh Data", "insertComicData")
    .addToUi();
}