[CmdletBinding()]
param(
    [string]$BaseUrl = 'http://localhost/api'
)

$ErrorActionPreference = 'Stop'

function Assert-Equal([object]$Actual, [object]$Expected, [string]$Message) {
    if ($Actual -ne $Expected) {
        throw "$Message Expected: $Expected; actual: $Actual"
    }
}

function Invoke-ApiJson {
    param(
        [string]$Method,
        [string]$Uri,
        [hashtable]$Headers,
        [object]$Body
    )

    $request = @{
        Method = $Method
        Uri = $Uri
        UseBasicParsing = $true
    }
    if ($Headers) { $request.Headers = $Headers }
    if ($null -ne $Body) {
        $request.ContentType = 'application/json'
        $request.Body = ($Body | ConvertTo-Json -Depth 10)
    }
    return Invoke-RestMethod @request
}

function Get-HttpStatusCode([System.Exception]$Exception) {
    if ($Exception.Response -and $Exception.Response.StatusCode) {
        return [int]$Exception.Response.StatusCode
    }
    return 0
}

$BaseUrl = $BaseUrl.TrimEnd('/')
$stamp = Get-Date -Format 'yyyyMMddHHmmssfff'
$email = "synthetic-$stamp@example.test"
$password = 'SyntheticJourney123!'
$headers = @{}

Write-Host "Using API: $BaseUrl"
Write-Host "Creating synthetic account: $email"
$signup = Invoke-ApiJson -Method Post -Uri "$BaseUrl/auth/signup" -Body @{
    email = $email
    password = $password
    full_name = 'Synthetic Journey User'
}
Assert-Equal $signup.email $email 'Signup returned the wrong email.'

$login = Invoke-ApiJson -Method Post -Uri "$BaseUrl/auth/login" -Body @{
    email = $email
    password = $password
}
if ([string]::IsNullOrWhiteSpace($login.access_token)) {
    throw 'Login did not return an access token.'
}
$headers = @{ Authorization = "Bearer $($login.access_token)" }
Write-Host 'OK signup and login'

$assessment = Invoke-ApiJson -Method Post -Uri "$BaseUrl/assessments" -Headers $headers -Body @{
    title = "Synthetic end-to-end assessment $stamp"
    description = 'Disposable local validation data.'
}
$assessmentId = $assessment.id
if (-not $assessmentId) { throw 'Assessment creation did not return an id.' }
Write-Host "OK assessment created: $assessmentId"

$questionnaires = Invoke-ApiJson -Method Get -Uri "$BaseUrl/assessments/questionnaires"
Assert-Equal $questionnaires.Count 4 'The live questionnaire schema should contain four categories.'

foreach ($questionnaire in $questionnaires) {
    $answers = @{}
    foreach ($question in $questionnaire.questions) {
        $bestOption = $question.options | Sort-Object -Property value -Descending | Select-Object -First 1
        $answers[$question.id] = [int]$bestOption.value
    }

    $result = Invoke-ApiJson -Method Post -Uri "$BaseUrl/assessments/$assessmentId/answers" -Headers $headers -Body @{
        category = $questionnaire.category
        answers = $answers
    }
    Assert-Equal $result.category $questionnaire.category "Answer submission failed for $($questionnaire.category)."
    Write-Host "OK category completed: $($questionnaire.category)"
}

$summary = Invoke-ApiJson -Method Get -Uri "$BaseUrl/assessments/$assessmentId/summary" -Headers $headers
Assert-Equal $summary.category_scores.Count 4 'The summary should contain four category scores.'
if ($summary.overall_score -lt 0 -or $summary.overall_score -gt 100) {
    throw "Summary score is outside the expected 0-100 range: $($summary.overall_score)"
}
Write-Host "OK summary rendered with overall score $($summary.overall_score)"

$csv = Invoke-WebRequest -UseBasicParsing -Uri "$BaseUrl/assessments/$assessmentId/export/csv" -Headers $headers
Assert-Equal $csv.StatusCode 200 'CSV export failed.'
if ($csv.RawContentLength -le 0) { throw 'CSV export returned an empty response.' }
Write-Host 'OK CSV export'

$pdf = Invoke-WebRequest -UseBasicParsing -Uri "$BaseUrl/assessments/$assessmentId/export/pdf" -Headers $headers
Assert-Equal $pdf.StatusCode 200 'PDF export failed.'
if ($pdf.RawContentLength -le 0) { throw 'PDF export returned an empty response.' }
Write-Host 'OK PDF export'

try {
    Invoke-RestMethod -Method Get -Uri "$BaseUrl/assessments" -UseBasicParsing | Out-Null
    throw 'An unauthenticated request unexpectedly succeeded.'
} catch {
    $status = Get-HttpStatusCode $_.Exception
    if ($status -ne 403) { throw "Unauthenticated request returned unexpected HTTP status $status." }
}
Write-Host 'OK unauthenticated access rejected'
Write-Host 'Synthetic API journey passed.'
