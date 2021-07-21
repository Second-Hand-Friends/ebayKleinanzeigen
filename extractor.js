// This script can be used to get the needed data fields, from manualy filling the kleinanzeigen
// form. Simply fill in all data in a Chrome browser, after clicking "Anzeige aufgeben", or "Bearbeiten"
// and open developer tools (right click on "Untersuchen" or press CMD+ALT+I). Select the Tab "console" 
// and copy the full text of this script into it and press RETURN
// it will show you the Data, like needed for an ad in config.json.

// NOTES
// Unfortunatly up to now the kleinanzeigen.py script have no handling for checkboxes, like 
// used i.e. for offers of cars. a handling for this need to be added to the kleinanzeigen.py script
// also a handling for posterType (PRIVATE or COMMERCIAL) is not implemented there up to now.
// it is not possible to get the original picture paths from your disk, for refference the links
// to the pictures on the ebay plattform will be included as "imgUsed"
// also "date_published" is only the time of running the script
// the "id" will be only included, when editing a still active offer, not when creating a new one. 

function getAd () {

let ad = {}

// get some data from javascript object "BelenConf"
 let cat1 = null,
     cat2 = null,
     cat3 = null,
     cat1Name = null,
     cat2Name = null,
     cat3Name = null,
     id = null

if (typeof BelenConf == "object") {

	// get categories
	cat1 = BelenConf.universalAnalyticsOpts.dimensions.dimension2
	cat2 = BelenConf.universalAnalyticsOpts.dimensions.dimension3
	cat3 = BelenConf.universalAnalyticsOpts.dimensions.dimension4
	cat1Name = BelenConf.universalAnalyticsOpts.dimensions.dimension90
	cat2Name = BelenConf.universalAnalyticsOpts.dimensions.dimension91
	cat3Name = BelenConf.universalAnalyticsOpts.dimensions.dimension92
	id = BelenConf.universalAnalyticsOpts.dimensions.dimension30

	if (id != null) ad.id = id

	let catCombo = ""
	if (cat1 != null && cat1 != "" && cat2 != null && cat2 != "" ) catCombo = cat1 + "/" + cat2
	if (cat3 != null && cat3 != "")	catCombo = catCombo + "/" + cat3 
	ad.caturl = "https://www.ebay-kleinanzeigen.de/p-kategorie-aendern.html#?path=" + catCombo + "&isParent=false"

	// get Versand
	ad.shipping_type = "NONE"
	if (cat2Name != null & cat2Name != "") {
		let selector = document.querySelector("#" + cat2Name.toLowerCase() + "\\.versand_s")
		if (selector != null && selector.options.selectedIndex == 1 ) ad.shipping_type = "SHIPPING"
		if (selector != null && selector.options.selectedIndex == 2 ) ad.shipping_type = "PICKUP"
	}
}

ad.date_published = new Date().toISOString()
ad.enabled = "1"


let adType1 = document.querySelector("#adType1")
let adType2 = document.querySelector("#adType2")
ad.type = "OFFER" // my Preset

if (adType1.checked) ad.type = adType1.value // "OFFER"
if (adType2.checked) ad.type = adType2.value // "WANTED"


ad.title = document.querySelector("#postad-title").value
ad.desc = document.querySelector("#pstad-descrptn").value
ad.price = document.querySelector("#pstad-price").value 

let priceType1 = document.querySelector("#priceType1")
let priceType2 = document.querySelector("#priceType2")
let priceType3 = document.querySelector("#priceType3")


ad.price_type = "FIXED" // my Preset
if (priceType1.checked)  ad.price_type = priceType1.value // "FIXED"
if (priceType2.checked)  ad.price_type = priceType2.value // "NEGOTIABLE"
if (priceType3.checked)  ad.price_type = priceType3.value // "GIVE_AWAY"

let imgUsed = []
document.querySelectorAll(".pictureupload-thumbnails img").forEach((img) => { 
	let bigImg = img.src.replace(/\$_\d{1,3}\./, "$_57.") // change the img link to the link for the largest image fromat from server (1600x1600 px, if original was such big)
	imgUsed.push(bigImg)
})
if (imgUsed.length > 0) ad.imgUsed = imgUsed;


ad.zipCode = document.querySelector("#pstad-zip").value

let posterTypePrivate = document.querySelector("#posterType-private")
let posterTypeCommercial = document.querySelector("#posterType-commercial")

if (posterTypePrivate.checked) ad.posterType = posterTypePrivate.value  // "PRIVATE"
if (posterTypeCommercial.checked) {
	ad.posterType = posterTypeCommercial.value  // "COMMERCIAL"
	// ad.imprint = document.querySelector("#pstad-imprnt-inpt").value
}


// Additional Attributes

let additional_category_options = {}
let count = 0
let attr = document.querySelectorAll("div.formgroup.pstad-attrs select, div.formgroup.pstad-attrs input")
if (attr != null) for (let i = 0; i < attr.length; i++ ) {
	if (attr[i].tagName == "INPUT") {
		if (attr[i].type == "text") {
			//console.log("INPUT text", attr[i].id, attr[i].value)
        		if (attr[i].value != "") {   // Add only items, which were filled with a value
        			additional_category_options[attr[i].id] = attr[i].value
				count++
			}
		}
		if (attr[i].type == "checkbox") {
			//console.log("INPUT checkbox", attr[i].id, attr[i].checked)
        		if (attr[i].checked) {   // Add only items, which are checked
        			additional_category_options[attr[i].id] = attr[i].checked
				count++
			}
		}

	}
	if ( attr[i].tagName == "SELECT") {
		//console.log("SELECT" ,attr[i].id, attr[i].selectedIndex, attr[i].options[attr[i].selectedIndex].text)
		if (attr[i].options[attr[i].selectedIndex].text.indexOf("wählen") < 0  ) { // add only selected items
			additional_category_options[attr[i].id] = attr[i].options[attr[i].selectedIndex].text
			count++
		}
	}
}
if (count > 0) ad.additional_category_options = additional_category_options

console.log(JSON.stringify(ad,null,4))
}

getAd()
