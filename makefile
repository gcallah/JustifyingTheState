export ABS_DIR = ./abstracts
export ADDR_DIR = ./addresses
export BIN_DIR = ./bin
export BIO_DIR = ./bios
export PROP_DIR = ./proposal
export PUB_DIR = ./to_publisher
export STRUCT_DIR = ./structure
export TMP_DIR = ./tmp
export WORD_DIR = ./word_docs
export ARCH_NAME = JustifyingTheState
export ARCH_FILE = $(PUB_DIR)/$(ARCH_NAME).zip
export AUTHOR_FILE = authors.txt
export MISSING_PROG = ./missing.py

FORCE:

prod: parts github

archive: $(ARCH_FILE)

$(ARCH_FILE): parts
	zip -r $(ARCH_FILE) $(WORD_DIR)/*.docx

github:
	# - means ignore errors on commit
	-git commit -a
	git push origin main

parts: abstracts bios toc proposal

whats_missing: missing_abs missing_addrs missing_bios 

missing_abs: FORCE
	$(MISSING_PROG) $(AUTHOR_FILE) $(ABS_DIR)
	
missing_addrs: FORCE
	$(MISSING_PROG) $(AUTHOR_FILE) $(ADDR_DIR)
	
missing_bios: FORCE
	$(MISSING_PROG) $(AUTHOR_FILE) $(BIO_DIR)
	
toc: $(WORD_DIR)/toc.docx

$(WORD_DIR)/toc.docx: toc.md
	pandoc -o $@ -f markdown -t docx $^

proposal: $(WORD_DIR)/prop.docx $(WORD_DIR)/palgrave.docx

$(WORD_DIR)/prop.docx: $(PROP_DIR)/prop.md
	pandoc -o $@ -f markdown -t docx $^

$(WORD_DIR)/palgrave.docx: $(PROP_DIR)/palgrave.md
	pandoc -o $@ -f markdown -t docx $^

abstracts: $(WORD_DIR)/abstracts.docx

$(WORD_DIR)/abstracts.docx: $(TMP_DIR)/abstracts.md
	pandoc -o $@ -f markdown -t docx $^

$(TMP_DIR)/abstracts.md: $(ABS_DIR)/*.md
	cat $^ > $@

bios: $(WORD_DIR)/bios.docx

$(WORD_DIR)/bios.docx: $(TMP_DIR)/bios.md
	pandoc -o $@ -f markdown -t docx $^

$(TMP_DIR)/bios.md: $(BIO_DIR)/*.md
	cat $^ > $@
