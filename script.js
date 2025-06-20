// updated_apps_script.gs
function insertComicDataWithPrices() {
  const url = "https://raw.githubusercontent.com/life423/comic-book-data/main/spiderman_comics_updated.json";
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  
  try {
    const response = UrlFetchApp.fetch(url);
    const comics = JSON.parse(response.getContentText());
    
    // Enhanced headers including new price data
    const headers = [
      "Title",
      "Series",
      "Issue #",
      "Year",
      "Original Grade",
      "Original Est. Value",
      "Ungraded Price",
      "6.0 Grade Price",
      "8.0 Grade Price",
      "Price Source",
      "Price Updated",
      "Key Notes",
      "Event",
      "Creator(s)"
    ];
    
    // Process data with new price information
    const rows = comics.map(comic => {
      const priceData = comic.PriceData || {};
      
      return [
        comic.Title,
        extractSeries(comic.Title),
        extractIssueNumber(comic.Title),
        extractYearFromTitle(comic.Title),
        comic.Grade,
        comic.EstValue,
        priceData.ungraded ? `$${priceData.ungraded}` : "N/A",
        priceData.grade_6_0 ? `$${priceData.grade_6_0}` : "N/A",
        priceData.grade_8_0 ? `$${priceData.grade_8_0}` : "N/A",
        priceData.source || "N/A",
        priceData.updated || "N/A",
        comic.KeyNotes || "N/A",
        comic.Event || "N/A",
        comic.Creator || "N/A"
      ];
    });
    
    // Clear and populate sheet
    sheet.clear();
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    
    if (rows.length > 0) {
      sheet.getRange(2, 1, rows.length, headers.length).setValues(rows);
    }
    
    // Apply formatting with price columns highlighted
    applyPriceDataFormatting(sheet, headers.length, rows.length);
    
    // Auto-resize columns
    sheet.autoResizeColumns(1, headers.length);
    
    // Add summary with new price data
    addPriceSummary(comics);
    
    SpreadsheetApp.getUi().alert(
      'Import Complete',
      `Imported ${comics.length} comics with updated price data.`,
      SpreadsheetApp.getUi().ButtonSet.OK
    );
    
  } catch (error) {
    Logger.log(`Error importing comic data: ${error.toString()}`);
    SpreadsheetApp.getUi().alert(`Error: ${error.toString()}`);
  }
}

function applyPriceDataFormatting(sheet, numCols, numRows) {
  if (numRows === 0) return;
  
  // Header formatting
  const headerRange = sheet.getRange(1, 1, 1, numCols);
  headerRange
    .setFontWeight("bold")
    .setBackground("#1f4e79")
    .setFontColor("#ffffff")
    .setHorizontalAlignment("center")
    .setBorder(true, true, true, true, true, true);
  
  // Price columns formatting (columns 7, 8, 9)
  if (numRows > 0) {
    // Highlight price columns with light green background
    const priceColumnsRange = sheet.getRange(2, 7, numRows, 3);
    priceColumnsRange.setBackground("#d9ead3");
    
    // Format all price columns
    const ungradedRange = sheet.getRange(2, 7, numRows, 1);
    const grade60Range = sheet.getRange(2, 8, numRows, 1);
    const grade80Range = sheet.getRange(2, 9, numRows, 1);
    
    [ungradedRange, grade60Range, grade80Range].forEach(range => {
      range.setHorizontalAlignment("right");
      range.setNumberFormat("$#,##0.00");
    });
    
    // Alternate row coloring for non-price columns
    for (let i = 2; i <= numRows + 1; i++) {
      if (i % 2 === 0) {
        // Only color non-price columns
        sheet.getRange(i, 1, 1, 6).setBackground("#f2f2f2");
        sheet.getRange(i, 10, 1, numCols - 9).setBackground("#f2f2f2");
      }
    }
  }
  
  // Freeze header row
  sheet.setFrozenRows(1);
}

function addPriceSummary(comics) {
  // Calculate average prices for each grade
  let ungradedPrices = [];
  let grade60Prices = [];
  let grade80Prices = [];
  
  comics.forEach(comic => {
    if (comic.PriceData) {
      if (comic.PriceData.ungraded) ungradedPrices.push(comic.PriceData.ungraded);
      if (comic.PriceData.grade_6_0) grade60Prices.push(comic.PriceData.grade_6_0);
      if (comic.PriceData.grade_8_0) grade80Prices.push(comic.PriceData.grade_8_0);
    }
  });
  
  const avgUngraded = ungradedPrices.length > 0 ? 
    ungradedPrices.reduce((a, b) => a + b, 0) / ungradedPrices.length : 0;
  const avg60 = grade60Prices.length > 0 ? 
    grade60Prices.reduce((a, b) => a + b, 0) / grade60Prices.length : 0;
  const avg80 = grade80Prices.length > 0 ? 
    grade80Prices.reduce((a, b) => a + b, 0) / grade80Prices.length : 0;
  
  Logger.log(`Average Prices - Ungraded: $${avgUngraded.toFixed(2)}, 6.0: $${avg60.toFixed(2)}, 8.0: $${avg80.toFixed(2)}`);
}

// Keep your existing helper functions
function extractSeries(title) {
  if (title.includes("Amazing Spider-Man")) return "Amazing Spider-Man";
  if (title.includes("Peter Parker, The Spectacular Spider-Man")) return "Peter Parker, The Spectacular Spider-Man";
  if (title.includes("Spectacular Spider-Man")) return "Spectacular Spider-Man";
  const match = title.match(/^([^#]+)/);
  return match ? match[1].trim() : "Unknown Series";
}

function extractIssueNumber(title) {
  const match = title.match(/#(\d+)/);
  return match ? parseInt(match[1]) : null;
}

function extractYearFromTitle(title) {
  // Your existing year extraction logic
  return "Est. " + (1963 + Math.floor(extractIssueNumber(title) / 12));
}