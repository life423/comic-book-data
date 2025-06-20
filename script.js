function insertComicData() {
  const url = "https://raw.githubusercontent.com/life423/comic-book-data/main/spiderman_comics_data.json";
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

  const response = UrlFetchApp.fetch(url);
  const comics = JSON.parse(response.getContentText());

  // Include all comics and compute numeric max price
  const prepared = comics.map(c => ({
    ...c,
    numericValue: parseInt(c.EstValue.split('–').pop().replace(/\D/g,''), 10)
  }));

  // Sort highest value first
  prepared.sort((a,b) => b.numericValue - a.numericValue);

  // Define headers without Slab Worthy?
  const headers = [
    "Title", "Year Released", "Grade",
    "Est. Value", "Key/Notes",
    "Event / 1st Appearance", "Creator(s)"
  ];

  const rows = prepared.map(c => [
    c.Title,
    extractYear(c.Title),
    c.Grade,
    c.EstValue,
    c.KeyNotes,
    c.Event,
    c.Creator
  ]);

  sheet.clearContents();
  sheet.getRange(1,1,1,headers.length).setValues([headers]);
  sheet.getRange(2,1,rows.length,headers.length).setValues(rows);

  applyFormatting(); 
}

function extractYear(title) {
  const map = {
    "#171": 1977,
    "#183": 1978,
    "#317": 1989,
    "#58": 1981,
    "#71": 1982,
    "Marvel Tales #115": 1980,
    "Marvel Team-Up #115": 1982
  };
  for (let key in map) {
    if (title.includes(key)) return map[key];
  }
  return "N/A";
}

function applyFormatting() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const width = sheet.getLastColumn();

  // Header styling
  sheet.getRange(1,1,1,width)
    .setFontWeight("bold")
    .setBackground("#4a86e8")
    .setFontColor("#ffffff");

  // Highlight top 3 issues
  if (sheet.getLastRow() >= 4) {
    sheet.getRange(2,1,3,width).setBackground("#d9ead3");
  }
}

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("Comic Tools")
    .addItem("Insert Comic Data", "insertComicData")
    .addToUi();
}
