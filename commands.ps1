
$url = "http://localhost:8001/generate_stories/"


$headers = @{ "Content-Type" = "application/json" }

# Execute the POST request to generate stories
Invoke-WebRequest -Uri $url -Method Post -Headers $headers
