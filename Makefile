copy-termux-shortcuts:
	@rm -r $(HOME)/.shortcuts/*
	@cp -a ./scripts/termux/. $(HOME)/.shortcuts/