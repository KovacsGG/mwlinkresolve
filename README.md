# MWLinkResolve

This one-shot python script fetches a MediaWiki wiki's redirect pages, and using that, compiles a list of all pages linking to redirect pages. It then edits those pages to instead link to the target of the redirect.

It doesn't resolve links to (redirects of) Files and links constructed with a Template. (Although it's not limited to main name-space pages, so if a Template hard-codes a link, it will revise that.)

Note, that Wikipedia guidelines discourage the "correction" of links pointing to redirect pages. This would cause a disproportionate amount of workload compared to what serving the redirect page does. It is theorized, however, that search-engine crawler budgets are chipped away at by 3xx HTTP responses, and so, resolving these links might mean improved visibility.
