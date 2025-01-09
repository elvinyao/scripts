$evaluateExpression(`
  {{$json["originalString"] ? 
    $json["originalString"].replace(/;$/, "").split(";").includes($json["targetString"] || "") 
    : false
  }}
`)
