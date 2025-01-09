$evaluateExpression(`
  {{$json["originalString"] ? 
    $json["originalString"].replace(/;$/, "").split(";").includes($json["targetString"] || "") 
    : false
  }}
`)


$evaluateExpression(`
  {{
    ($json["originalString"] || "")
      .trim()
      .replace(/;$/, "")
      .split(";")
      .map(item => item.trim())
      .includes(($json["targetString"] || "").trim())
  }}
`)
