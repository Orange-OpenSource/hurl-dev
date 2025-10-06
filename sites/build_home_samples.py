#!/usr/bin/env python3
import re
from pathlib import Path


class Sample:
    name: str
    src: str
    html: str

    def __init__(self, name: str, src: str):
        self.name = name
        src_padded = src
        # Count number of line in src, add padding if necessary
        nl = src_padded.count("\n")
        max_line = 14
        if nl < max_line:
            src_padded += "\n" * (max_line - nl)
        self.src = src_padded
        html = '<pre><code class="language-hurl">'
        html += src_padded
        html += "</code></pre>\n"
        self.html = html


def make_home_samples():
    samples = [
        Sample(
            name="Request Headers",
            src="""\
# A simple GET with headers            
GET https://example.org/news
User-Agent: Mozilla/5.0 
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
""",
        ),
        Sample(
            name="Chaining Requests",
            src="""\
# Chaining requests is easy, responses are optional
GET https://example.org/api/health

GET https://example.org/api/step1
HTTP 200

GET https://example.org/api/step2

GET https://example.org/api/step3
""",
        ),
        Sample(
            name="Query Params",
            src="""\
# Use query params in the URL:
GET https://example.org/news?order=newest&search=something%20to%20search&count=100


# Or with a query param section:            
GET https://example.org/news
[Query]
order: newest
search: something to search
count: 100
""",
        ),
        Sample(
            name="Basic Authentication",
            src="""\
GET https://example.org/protected
[BasicAuth]
bob: secret


# One can also use an Authorization header
# Authorization header value can be computed with `echo -n 'bob:secret' | base64`
GET https://example.org/protected
Authorization: Basic Ym9iOnNlY3JldA==
""",
        ),
        Sample(
            name="Form",
            src="""\
# Sending form data
POST https://example.org/contact
[Form]
default: false
token: {{token}}
email: john.doe@rookie.org
number: 33611223344
""",
        ),
        Sample(
            name="Multipart",
            src="""\
POST https://example.org/upload
[Multipart]
field1: value1
field2: file,example.txt;
# One can specify the file content type:
field3: file,example.zip; application/zip
""",
        ),
        Sample(
            name="Cookies",
            src="""\
# Requests in the same Hurl file share the cookie storage
# Cookies can also be set per request    
GET http://localhost:8000/cookies/set-multiple-request-cookies
[Cookies]
user1: Bob
user2: Bill
user3: {{name}}
HTTP 200

# Or we can simply use a Cookie header
GET https://example.org/index.html
Cookie: theme=light; sessionToken=abc123
""",
        ),
        Sample(
            name="Capture Data",
            src="""\
# Go home and capture token
GET https://example.org
HTTP 200
[Captures]
csrf_token: xpath "string(//meta[@name='_csrf_token']/@content)"


# Do login!
POST https://example.org/login
X-CSRF-TOKEN: {{csrf_token}}
[Form]
user: toto
password: 1234
HTTP 302
""",
        ),
        Sample(
            name="JSON Body",
            src="""\
# Create a new doggy thing with JSON body.
# JSON body can be inlined:
POST https://example.org/api/dogs
{
    "id": 0,
    "name": "Frieda",
    "picture": "images/scottish-terrier.jpeg",
    "age": 3,
    "breed": "Scottish Terrier",
    "location": "Lisco, Alabama"
}
""",
        ),
        Sample(
            name="SOAP / XML Body",
            src="""\
# Like JSON body, XML bidy can be inlined to use SOAP APIs:
POST https://example.org/InStock
Content-Type: application/soap+xml; charset=utf-8
SOAPAction: "http://www.w3.org/2003/05/soap-envelope"
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:m="http://example.net">
  <soap:Header></soap:Header>
  <soap:Body>
    <m:GetStockPrice>
      <m:StockName>GOOG</m:StockName>
    </m:GetStockPrice>
  </soap:Body>
</soap:Envelope>
""",
        ),
        Sample(
            name="GraphQL",
            src="""\
# GraphQL queries are supported, even with variables            
POST https://example.org/starwars/graphql
```graphql
{
  human(id: "1000") {
    name
    appearsIn
    height(unit: FOOT)
  }
}
```
""",
        ),
        Sample(
            name="Text Body",
            src='''\
POST https://example.org/models
Content-Type: text/csv
```
Year,Make,Model,Description,Price
1997,Ford,E350,"ac, abs, moon",3000.00
1999,Chevy,"Venture ""Extended Edition""","",4900.00
1999,Chevy,"Venture ""Extended Edition, Very Large""",,5000.00
1996,Jeep,Grand Cherokee,"MUST SELL! air, moon roof, loaded",4799.00
```
''',
        ),
        Sample(
            name="Binary Body",
            src="""\
POST https://example.org
# Some random comments before body
base64,TG9yZW0gaXBzdW0gZG9sb3Igc2l0IGFtZXQsIGNvbnNlY3RldHVyIG
FkaXBpc2NpbmcgZWxpdC4gSW4gbWFsZXN1YWRhLCBuaXNsIHZlbCBkaWN0dW0g
aGVuZHJlcml0LCBlc3QganVzdG8gYmliZW5kdW0gbWV0dXMsIG5lYyBydXRydW
0gdG9ydG9yIG1hc3NhIGlkIG1ldHVzLiA=;

# Or use a file
POST https://example.org
file,data.bin;
""",
        ),
        Sample(
            name="Response Headers",
            src="""\
# Using implicit response asserts 
GET https://example.org/index.html
HTTP 200
Set-Cookie: theme=light
Set-Cookie: sessionToken=abc123; Expires=Wed, 09 Jun 2021 10:18:14 GMT

# Or explicit response asserts
GET https://example.org
HTTP 302
[Asserts]
header "Location" contains "www.example.net"
""",
        ),
        Sample(
            name="Testing Status Code",
            src="""\
# Testing 200 OK
GET https://example.org/order/435
HTTP 200


# Testing status code is in a 200-300 range
GET https://example.org/order/435
HTTP *
[Asserts]
status >= 200
status < 300
""",
        ),
        Sample(
            name="Testing HTTP Version",
            src="""\
# You can explicitly test HTTP version 1.0, 1.1, 2 or 3:
GET https://example.org/http3
HTTP/3 200

GET https://example.org/http2
HTTP/2 200

# Or simply use HTTP to not test version!
GET https://example.org/http2
HTTP 200
""",
        ),
        Sample(
            name="Testing XPath",
            src="""\
# XPath asserts can be used to check HTML content            
GET https://example.org
HTTP 200
Content-Type: text/html; charset=UTF-8
[Asserts]
xpath "string(/html/head/title)" contains "Example" # Check title
xpath "count(//p)" == 2                             # Check the number of p
xpath "//p" count == 2                              # Similar assert for p
xpath "boolean(count(//h2))" == false               # Check there is no h2  
xpath "//h2" not exists                             # Similar assert for h2
xpath "string(//div[1])" matches /Hello.*/
""",
        ),
        Sample(
            name="Testing JSONPath",
            src="""\
# Testing a JSON response with JSONPath
GET https://example.org/api/tests/4567
HTTP 200
[Asserts]
jsonpath "$.status" == "RUNNING"    # Check the status code
jsonpath "$.tests" count == 25      # Check the number of items
jsonpath "$.id" matches /\\d{4}/     # Check the format of the id
""",
        ),
        Sample(
            name="Testing Set-Cookie",
            src="""\
GET http://myserver.com/home
HTTP 200
[Asserts]
cookie "JSESSIONID" == "8400BAFE2F66443613DC38AE3D9D6239"
cookie "JSESSIONID[Value]" == "8400BAFE2F66443613DC38AE3D9D6239"
cookie "JSESSIONID[Expires]" contains "Wed, 13 Jan 2021"
cookie "JSESSIONID[Secure]" exists
cookie "JSESSIONID[HttpOnly]" exists
cookie "JSESSIONID[SameSite]" == "Lax"
""",
        ),
        Sample(
            name="Testing Bytes",
            src="""\
# Check the SHA-256 response body hash:             
GET https://example.org/data.tar.gz
HTTP 200
[Asserts]
sha256 == hex,039058c6f2c0cb492c533b0a4d14ef77cc0f78abccced5287d84a1a2011cfb81;

# Checking Byte Order Mark (BOM) in Response Body
GET https://example.org/data.bin
HTTP 200
[Asserts]
bytes startsWith hex,efbbbf;
""",
        ),
        Sample(
            name="SSL Certificate",
            src="""\
# Check attributes of the SSL certificate
GET https://example.org
HTTP 200
[Asserts]
certificate "Subject" == "CN=example.org"
certificate "Issuer" == "C=US, O=Let's Encrypt, CN=R3"
certificate "Expire-Date" daysAfterNow > 15
certificate "Serial-Number" matches /[\\da-f]+/
""",
        ),
        Sample(
            name="Polling / Retry",
            src="""\
# Pull job status until it is completed
GET https://api.example.org/jobs/{{job_id}}
[Options]
retry: 10  # maximum number of retry, -1 for unlimited
retry-interval: 300ms
HTTP 200
[Asserts]
jsonpath "$.state" == "COMPLETED"
""",
        ),
        Sample(
            name="IP Address",
            src="""\
GET https://example.org
HTTP 200
[Asserts]
ip == "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
ip startsWith "2001"

GET https://example.org
[Options]
ipv4: true
HTTP 200
[Asserts]
ip not isIpv6
""",
        ),
    ]

    feature_sample = 7

    select_html = ""
    select_html += '<div class="home-picker">\n'
    select_html += (
        '<label class="home-picker-label" for="home-samples">Choose example</label>\n'
    )
    select_html += '<select id="home-samples" name="samples">\n'
    for idx, sample in enumerate(samples):
        if idx == feature_sample:
            select = " selected"
        else:
            select = ""
        select_html += (
            f'    <option value="home-sample-{idx}"{select}>{sample.name}</option>\n'
        )
    select_html += "</select>\n"
    select_html += "</div>\n"
    select_html += '<div class="home-sample">\n'
    select_html += samples[feature_sample].html
    select_html += "</div>\n"

    samples_html = '<div hidden aria-hidden="true">\n'
    for idx, sample in enumerate(samples):
        samples_html += f'<div class="home-sample-{idx}">\n'
        samples_html += sample.html
        samples_html += "</div>\n"
    samples_html += "</div>\n"

    # Replace first home sample with this new sample
    home_path = Path("hurl.dev", "_site", "index.html")
    home_html = home_path.read_text(encoding="utf-8")
    r = re.compile(
        r'(<pre><code class="language-hurl">.*?</code></pre>)', flags=re.DOTALL
    )
    home_html = r.sub(lambda x: select_html + samples_html, home_html, count=1)
    home_path.write_text(home_html, encoding="utf-8")


if __name__ == "__main__":
    make_home_samples()
