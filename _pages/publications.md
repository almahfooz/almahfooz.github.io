---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---

{% if site.author.googlescholar %}
    <div class="wordwrap">You can also find my articles on <a href="{{site.author.googlescholar}}">Google Scholar</a>.
    <a href="https://www.webofscience.com/wos/author/record/HMO-8713-2023">Web of Science</a>.
    <a href="https://www.scopus.com/authid/detail.uri?authorId=57193214675">Scopus</a>.
  </div>  
{% endif %}

{% include base_path %}

{% for post in site.publications reversed %}
  {% include archive-single.html %}
{% endfor %}
