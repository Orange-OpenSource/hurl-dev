'use strict';

class Search {

    constructor(inputId, resultListId, resultTextId) {
        this.inputId = inputId;
        this.resultListId = resultListId;
        this.resultTextId = resultTextId;
        this.registerInput();
    }

    getQueryParam() {
        let parsedUrl = new URL(window.location.href);
        return parsedUrl.searchParams.get("query");
    }

    getSearchInput() {
        return document.getElementById(this.inputId);
    }

    registerInput() {
        window.addEventListener("load", (event) => {
            this.getSearchInput().onkeyup = (event) => {
                this.onKeyup(event);
            };
        });
    }

    onKeyup(event) {
        let query = event.target.value.toLowerCase().trim();
        this.searchQuery(query);
    }

    searchQuery(query) {
        if (this.index === undefined) {
            return
        }
        let hits = this.index.hits[query];
        let resultElmt = document.getElementById(this.resultListId);
        resultElmt.textContent = "";
        if (hits === undefined) {
            this.updateResultText(0);
            return;
        }

        this.updateResultText(hits.length);

        let ul = document.createElement("ul");
        resultElmt.appendChild(ul);

        for (let i = 0; i < hits.length; i++) {
            let ref = this.index.refs[hits[i]];
            let li = this.buildResultNode(ref, query);
            ul.appendChild(li);
        }
    }

    updateResultText(count) {
        let resultTextElmt = document.getElementById(this.resultTextId);
        if (count === 0) {
            resultTextElmt.innerText = "No results";
        } else {
            resultTextElmt.innerText = `Results (${count})`;
        }
    }

    loadIndex() {
        let xhr = new XMLHttpRequest();
        xhr.open("GET", "/assets/data/index.json", true);
        xhr.onload = (e) => {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    this.index = JSON.parse(xhr.responseText);
                    let query = this.getQueryParam();

                    if (query !== null) {
                        this.searchQuery(query);
                        let input = this.getSearchInput();
                        input.value = query;
                    }
                }
            }
        };
        xhr.send(null);
    }

    buildResultNode(hit, query) {
        let {page_title, page_url, anchor_title, anchor_url, content, search, start} = hit;
        let li = document.createElement("li");
        let contentMarked = this.highlightPos(content, query, start);
        li.innerHTML = `<h3><a href="${anchor_url}">${page_title} &gt; ${anchor_title}</a></h3>
                        <p>${contentMarked}</p>`;

        //let json = JSON.stringify(hit, null, 4);
        //li.innerHTML += `<p><pre><code>${json}</code></pre></p>`;

        return li;
    }

    highlight(str, query) {
        let re = new RegExp(`(${query})`, "gi");
        return str.replace(re, `<span class="marked">$1</span>`);
    }

    highlightPos(str, query, start) {
        let count = query.length,
            end = start + count,
            prefix = str.slice(0, start),
            mark = str.slice(start, end),
            suffix = str.slice(end);
        return `${prefix}<span class="marked">${mark}</span>${suffix}`;
    }

}

let search = new Search("search-input", "search-results", "results");
search.loadIndex();
window.hurl = {};
window.hurl.search = search;
