
from doc_store_vector_search_mcp.etl.splitters.html import HTMLSemanticPreservingSplitter

body = """
<body>
<div class="tabbed-content">
<div class="tabbed-block">
<div class="language-python highlight"><pre id="__code_6"><span></span><button class="md-clipboard md-icon" title="Copy to clipboard" data-clipboard-target="#__code_6 &gt; code"></button><code><span class="kn">from</span><span class="w"> </span><span class="nn">typing</span><span class="w"> </span><span class="kn">import</span> <span class="n">Annotated</span><span class="p">,</span> <span class="n">Any</span>

<span class="kn">from</span><span class="w"> </span><span class="nn">pydantic</span><span class="w"> </span><span class="kn">import</span> <span class="n">BaseModel</span><span class="p">,</span> <span class="n">PlainValidator</span>


<span class="k">def</span><span class="w"> </span><span class="nf">val_number</span><span class="p">(</span><span class="n">value</span><span class="p">:</span> <span class="n">Any</span><span class="p">)</span> <span class="o">-&gt;</span> <span class="n">Any</span><span class="p">:</span>
    <span class="k">if</span> <span class="nb">isinstance</span><span class="p">(</span><span class="n">value</span><span class="p">,</span> <span class="nb">int</span><span class="p">):</span>
        <span class="k">return</span> <span class="n">value</span> <span class="o">*</span> <span class="mi">2</span>
    <span class="k">else</span><span class="p">:</span>
        <span class="k">return</span> <span class="n">value</span>


<span class="k">class</span><span class="w"> </span><span class="nc">Model</span><span class="p">(</span><span class="n">BaseModel</span><span class="p">):</span>
    <span class="n">number</span><span class="p">:</span> <span class="n">Annotated</span><span class="p">[</span><span class="nb">int</span><span class="p">,</span> <span class="n">PlainValidator</span><span class="p">(</span><span class="n">val_number</span><span class="p">)]</span>


<span class="nb">print</span><span class="p">(</span><span class="n">Model</span><span class="p">(</span><span class="n">number</span><span class="o">=</span><span class="mi">4</span><span class="p">))</span>
<span class="c1">#&gt; number=8</span>
<span class="nb">print</span><span class="p">(</span><span class="n">Model</span><span class="p">(</span><span class="n">number</span><span class="o">=</span><span class="s1">'invalid'</span><span class="p">))</span>  <span class="c1"><aside class="md-annotation" tabindex="0" style="--md-tooltip-x: 289px; --md-tooltip-y: 363px; --md-tooltip-0: -46px;" data-md-visible=""><div class="md-tooltip md-tooltip--active" id="__code_6_annotation_1" role="tooltip"><div class="md-tooltip__inner md-typeset">Although <code>'invalid'</code> shouldn't validate against the <code>int</code> type, Pydantic accepts the input.</div></div><a href="#__code_6_annotation_1" class="md-annotation__index" tabindex="-1"><span data-md-annotation-id="1"></span></a></aside></span>
<span class="c1">#&gt; number='invalid'</span>
</code><button class="run-code-btn play-btn" title="Run code"></button><button class="run-code-btn reset-btn run-code-hidden" title="Reset code"></button></pre></div>
<ol hidden="">
<li></li>
</ol>
</div>
<div class="tabbed-block">
<div class="language-python highlight"><pre id="__code_7"><span></span><button class="md-clipboard md-icon" title="Copy to clipboard" data-clipboard-target="#__code_7 &gt; code"></button><code><span class="kn">from</span><span class="w"> </span><span class="nn">typing</span><span class="w"> </span><span class="kn">import</span> <span class="n">Any</span>

<span class="kn">from</span><span class="w"> </span><span class="nn">pydantic</span><span class="w"> </span><span class="kn">import</span> <span class="n">BaseModel</span><span class="p">,</span> <span class="n">field_validator</span>


<span class="k">class</span><span class="w"> </span><span class="nc">Model</span><span class="p">(</span><span class="n">BaseModel</span><span class="p">):</span>
    <span class="n">number</span><span class="p">:</span> <span class="nb">int</span>

    <span class="nd">@field_validator</span><span class="p">(</span><span class="s1">'number'</span><span class="p">,</span> <span class="n">mode</span><span class="o">=</span><span class="s1">'plain'</span><span class="p">)</span>
    <span class="nd">@classmethod</span>
    <span class="k">def</span><span class="w"> </span><span class="nf">val_number</span><span class="p">(</span><span class="bp">cls</span><span class="p">,</span> <span class="n">value</span><span class="p">:</span> <span class="n">Any</span><span class="p">)</span> <span class="o">-&gt;</span> <span class="n">Any</span><span class="p">:</span>
        <span class="k">if</span> <span class="nb">isinstance</span><span class="p">(</span><span class="n">value</span><span class="p">,</span> <span class="nb">int</span><span class="p">):</span>
            <span class="k">return</span> <span class="n">value</span> <span class="o">*</span> <span class="mi">2</span>
        <span class="k">else</span><span class="p">:</span>
            <span class="k">return</span> <span class="n">value</span>


<span class="nb">print</span><span class="p">(</span><span class="n">Model</span><span class="p">(</span><span class="n">number</span><span class="o">=</span><span class="mi">4</span><span class="p">))</span>
<span class="c1">#&gt; number=8</span>
<span class="nb">print</span><span class="p">(</span><span class="n">Model</span><span class="p">(</span><span class="n">number</span><span class="o">=</span><span class="s1">'invalid'</span><span class="p">))</span>  <span class="c1"><aside class="md-annotation" tabindex="0" style=""><div class="md-tooltip" id="__code_7_annotation_1" role="tooltip"><div class="md-tooltip__inner md-typeset">Although <code>'invalid'</code> shouldn't validate against the <code>int</code> type, Pydantic accepts the input.</div></div><a href="#__code_7_annotation_1" class="md-annotation__index" tabindex="-1"><span data-md-annotation-id="1"></span></a></aside></span>
<span class="c1">#&gt; number='invalid'</span>
</code><button class="run-code-btn play-btn" title="Run code"></button><button class="run-code-btn reset-btn run-code-hidden" title="Reset code"></button></pre></div>
<ol hidden="">
<li></li>
</ol>
</div>
</div>
</body>
"""


splitter = HTMLSemanticPreservingSplitter(
    headers_to_split_on=[],
    child_elements_to_preserve=["code"],
)


if __name__ == "__main__":
    documents = splitter.split_text(body)
    for document in documents:
        print("-----------------")
        print(document.page_content)
        print("-----------------")
        preserved_elements = document.metadata.get("delayed_replacements", {})
        for key, value in preserved_elements.items():
            print(f"{key}: {value}")
        print("-----------------")
