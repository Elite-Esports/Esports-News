# URL for generating stories from your FastAPI application
$url = "http://localhost:8001/generate_stories/"

# Headers for the POST request (adjust if you have different headers)
$headers = @{ "Content-Type" = "application/json" }

# Execute the POST request to generate stories
Invoke-WebRequest -Uri $url -Method Post -Headers $headers
