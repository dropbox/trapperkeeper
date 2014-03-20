.PHONY: handlebars

handlebars:
	handlebars -mf trapdoor/static/js/hb_templates.min.js trapdoor/handlebars/*.handlebars
