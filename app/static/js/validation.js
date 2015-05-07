console.log("Validation loaded");

var gse =  /^https:\/\/docs.google.com\/spreadsheets/

$("#gs_form").submit(function (event) {

  if (gse.exec($("#url").val())) {
    console.log(gse.exec($("#url").val()));
    $( "span" ).text( "Validado" ).show();
    return;
  }
  console.log($("#url"));
  $( "span" ).text( "La URL proporcionada no corresponde a Google spreadsheet" ).show().fadeIn( 1000 );
  event.preventDefault();
});
