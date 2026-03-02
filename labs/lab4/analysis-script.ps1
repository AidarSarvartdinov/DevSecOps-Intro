$ErrorActionPreference = "Stop"

$analysisFile = "labs/lab4/analysis/sbom-analysis.txt"
New-Item -ItemType File -Force -Path $analysisFile | Out-Null

Add-Content -Path $analysisFile -Value "=== SBOM Component Analysis ==="
Add-Content -Path $analysisFile -Value ""

Add-Content -Path $analysisFile -Value "Syft Package Counts:"
jq -r '.artifacts[] | .type' labs/lab4/syft/juice-shop-syft-native.json | Group-Object -NoElement | Sort-Object Count -Descending | ForEach-Object { "   $($_.Count) $($_.Name)" } | Add-Content -Path $analysisFile

Add-Content -Path $analysisFile -Value ""
Add-Content -Path $analysisFile -Value "Trivy Package Counts:"
jq -r '.Results[] as $result | $result.Packages[]? | "\($result.Target // `"Unknown`") - \(.Type // `"unknown`")"' labs/lab4/trivy/juice-shop-trivy-detailed.json | Group-Object -NoElement | Sort-Object Count -Descending | ForEach-Object { "   $($_.Count) $($_.Name)" } | Add-Content -Path $analysisFile

Add-Content -Path $analysisFile -Value ""
Add-Content -Path $analysisFile -Value "=== License Analysis ==="
Add-Content -Path $analysisFile -Value ""

Add-Content -Path $analysisFile -Value "Syft Licenses:"
jq -r '.artifacts[]? | select(.licenses != null) | .licenses[]? | .value' labs/lab4/syft/juice-shop-syft-native.json | Group-Object -NoElement | Sort-Object Count -Descending | ForEach-Object { "   $($_.Count) $($_.Name)" } | Add-Content -Path $analysisFile

Add-Content -Path $analysisFile -Value ""
Add-Content -Path $analysisFile -Value "Trivy Licenses (OS Packages):"
jq -r '.Results[] | select(.Class // `"`" | contains(`"os-pkgs`")) | .Packages[]? | select(.Licenses != null) | .Licenses[]?' labs/lab4/trivy/juice-shop-trivy-detailed.json | Group-Object -NoElement | Sort-Object Count -Descending | ForEach-Object { "   $($_.Count) $($_.Name)" } | Add-Content -Path $analysisFile

Add-Content -Path $analysisFile -Value ""  
Add-Content -Path $analysisFile -Value "Trivy Licenses (Node.js):"
jq -r '.Results[] | select(.Class // `"`" | contains(`"lang-pkgs`")) | .Packages[]? | select(.Licenses != null) | .Licenses[]?' labs/lab4/trivy/juice-shop-trivy-detailed.json | Group-Object -NoElement | Sort-Object Count -Descending | ForEach-Object { "   $($_.Count) $($_.Name)" } | Add-Content -Path $analysisFile

$syftLicensesFile = "labs/lab4/syft/juice-shop-licenses.txt"
New-Item -ItemType File -Force -Path $syftLicensesFile | Out-Null
Add-Content -Path $syftLicensesFile -Value "Extracting licenses from Syft SBOM..."
jq -r '.artifacts[] | select(.licenses != null and (.licenses | length > 0)) | "\(.name) | \(.version) | \(.licenses | map(.value) | join(`", `"))"' labs/lab4/syft/juice-shop-syft-native.json | Add-Content -Path $syftLicensesFile
