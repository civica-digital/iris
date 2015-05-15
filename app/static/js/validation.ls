console.log "Validation loaded"

let gse = /^https:\/\/docs.google.com\/spreadsheets/g
  (event) <- $ "\#gs_form" .submit
  if gse.exec($ "\#url" .val!)
    console.log gse.exec($ "\#url" .val!)

    $ "span"
      .text "Validado"
      .show!

    console.log $ "\#url"
    return

  $ "span"
    .text "La URL proporcionada no corresponde a Google spreadsheet"
    .show!
    .fadeIn 1000

  event.preventDefault!
