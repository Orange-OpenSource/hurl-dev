'use strict';

function groupBy(xs, key) {
    const map = new Map()
    for (const x of xs) {
        if (map.has(x[key])) {
            map.get(x[key]).push(x);
        } else {
            map.set(x[key], [x]);
        }
    }
    return map
}

/**
 * This class implements a local search for the documentation.
 * When searching query on the documentation, there is no server involved
 * and the whole search is processed locally in the browser.
 * To do so, a search index is loaded (/assets/data/index.json). The search index has the following structure:
 * - hits: a key/value dictionary where key is a search token and value a list of search results (id of ref)
 * - refs: search results
 * - pages: indexed pages
 * - anchors: index anchors
 *
 * Ref structure:
 * - anchor: id of the anchor
 * - content: text content of the search result
 * - page: id of the page
 * - start: start index of the result in the content
 *
 * Page structure:
 * - section: name of the section containing this page
 * - title: page title
 * - url: page url
 *
 * Anchor structire:
 * - title: anchor title
 * - url: anchor url
 */
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
        this.searchQuery(event.target.value);
    }

    searchQuery(query) {
        if (this.index === undefined) {
            return
        }
        const queryNormalized = query.toLowerCase().trim();
        const hits = this.index.hits[queryNormalized];
        const resultElmt = document.getElementById(this.resultListId);
        resultElmt.textContent = "";
        if (hits === undefined) {
            this.updateResultText(0);
            return;
        }

        this.updateResultText(hits.length);

        let div = document.createElement("div");
        resultElmt.appendChild(div);

        // Denormalized hits:
        const {anchors, pages, refs} = this.index;
        const results = hits.map(
            it => {
                const ref = refs[it];
                const anchorId = ref.anchor;
                const pageId = ref.page;
                const anchor = anchors[anchorId];
                const page = pages[pageId];
                return {
                    anchorTitle: anchor.title,
                    anchorUrl: anchor.url,
                    content: ref.content,
                    pageTitle: page.title,
                    pageSection: page.section,
                    pageUrl: page.url,
                    start: ref.start
                }
            });
        // Group results by section:
        const resultsMap = groupBy(results, "pageSection");
        resultsMap.forEach((value, key) => {
            const details = document.createElement("details");
            details.setAttribute("open", "");
            div.appendChild(details);

            const summary = document.createElement("summary");
            details.appendChild(summary);

            const h3 = document.createElement("h3");
            h3.innerHTML = `${key} (${value.length})`;
            summary.appendChild(h3);

            const ul = document.createElement("ul");
            details.appendChild(ul);

            for(const result of value) {
                const li = this.buildResultNode(result, query);
                ul.appendChild(li);
            }
        });
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
        const xhr = new XMLHttpRequest();
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

    buildResultNode(result, query) {
        const li = document.createElement("li");
        const contentMarked = this.highlightPos(result.content, query, result.start);
        li.innerHTML = `<p class="search-result-link"><a href="${result.anchorUrl}">${result.pageTitle} &gt; ${result.anchorTitle}</a></p>
                        <p>${contentMarked}</p>`;

        //let json = JSON.stringify(hit, null, 4);
        //li.innerHTML += `<p><pre><code>${json}</code></pre></p>`;

        return li;
    }

    highlight(str, query) {
        const re = new RegExp(`(${query})`, "gi");
        return str.replace(re, `<span class="marked">$1</span>`);
    }

    highlightPos(str, query, start) {
        const count = query.length,
            end = start + count,
            prefix = str.slice(0, start),
            mark = str.slice(start, end),
            suffix = str.slice(end);
        return `${prefix}<span class="marked">${mark}</span>${suffix}`;
    }

}

const search = new Search("search-input", "search-results", "results");
search.loadIndex();
window.hurl = {};
window.hurl.search = search;
