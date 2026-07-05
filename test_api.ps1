# Test CivicTrust AI API
Write-Host "🏛️ Testing CivicTrust AI API..." -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "`n📌 Test 1: Health Check" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "   ✅ Status: $($response.status)" -ForegroundColor Green
    Write-Host "   Version: $($response.version)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

# Test 2: Chat API
Write-Host "`n📌 Test 2: Chat API" -ForegroundColor Yellow
try {
    $body = @{
        message = "Apa syarat membuat KTP?"
        language = "id"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/chat" -Method Post -Body $body -ContentType "application/json"
    Write-Host "   ✅ Jawaban: $($response.answer)" -ForegroundColor Green
    Write-Host "   Trust Score: $($response.trust_score)" -ForegroundColor Green
    Write-Host "   Session ID: $($response.session_id)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

# Test 3: Fact Check API
Write-Host "`n📌 Test 3: Fact Check API" -ForegroundColor Yellow
try {
    $body = @{
        statement = "Vaksin COVID-19 aman digunakan"
        language = "id"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/fact-check" -Method Post -Body $body -ContentType "application/json"
    Write-Host "   ✅ Verdict: $($response.verdict)" -ForegroundColor Green
    Write-Host "   Confidence: $($response.confidence)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

# Test 4: Translation API
Write-Host "`n📌 Test 4: Translation API" -ForegroundColor Yellow
try {
    $body = @{
        text = "Selamat pagi"
        source_language = "id"
        target_language = "en"
    } | ConvertTo-Json
    
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/translate" -Method Post -Body $body -ContentType "application/json"
    Write-Host "   ✅ Hasil: $($response.translated_text)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

# Test 5: Analytics API
Write-Host "`n📌 Test 5: Analytics API" -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/analytics" -Method Get
    Write-Host "   ✅ Total Queries: $($response.total_queries)" -ForegroundColor Green
    Write-Host "   Accuracy: $($response.accuracy)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

Write-Host "`n✅ Testing Selesai!" -ForegroundColor Cyan