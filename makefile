include $(INI_HOME)/common.mk

export ABS_DIR = ./abstracts
export ADDR_DIR = ./addresses
export BIN_DIR = ./bin
export BIO_DIR = ./bios
export CHAP_DIR = ./chapters
export PDF_DIR = ./chap_pdfs
export KWORD_DIR = ./keywords
export PERM_DIR = ./permissions
export PROP_DIR = ./proposal
export PUB_DIR = ./submission
export STRUCT_DIR = ./structure
export TMP_DIR = ./tmp
export ARCH_NAME = JustifyingTheState
export ARCH_DIR = ./archive
export ARCH_FILE = $(ARCH_DIR)/$(ARCH_NAME).zip
export ARCH_PROG = zip
export AUTHOR_FILE = authors.txt
export MISSING_PROG = ./missing.py

FORCE:

prod: parts

archive: $(ARCH_FILE)

$(ARCH_FILE): FORCE
	$(ARCH_PROG) -r $(ARCH_FILE) $(PUB_DIR)/*

github:
	# - means ignore errors on commit
	-git commit -a
	git push origin main

parts: abstracts addresses all_chaps bios keywords permissions toc

keywords: FORCE
	./add_keyword_info.py

$(PUB_DIR)/toc.docx: toc.md
	pandoc -o $@ -f markdown -t docx $^

abstracts: $(PUB_DIR)/abstracts.docx

$(PUB_DIR)/abstracts.docx: $(TMP_DIR)/abstracts.md
	pandoc -o $@ -f markdown -t docx $^

$(TMP_DIR)/abstracts.md: $(ABS_DIR)/*.md
	cat $^ > $@

addresses: $(PUB_DIR)/addresses.docx

$(PUB_DIR)/addresses.docx: $(TMP_DIR)/addresses.md
	pandoc -o $@ -f markdown -t docx $^

$(TMP_DIR)/addresses.md: $(ADDR_DIR)/*.md
	cat $^ > $@

bios: $(PUB_DIR)/bios.docx

$(PUB_DIR)/bios.docx: $(TMP_DIR)/bios.md
	pandoc -o $@ -f markdown -t docx $^

$(TMP_DIR)/bios.md: $(BIO_DIR)/*.md
	cat $^ > $@

CHAP_FILES := $(wildcard $(CHAP_DIR)/*.docx)

$(PDF_DIR)/%.pdf: $(CHAP_DIR)/%.docx
		pandoc $< -o $@ --pdf-engine=xelatex

all_chaps: $(CHAP_FILES:$(CHAP_DIR)/%.docx=$(PDF_DIR)/%.pdf)
	./add_chap_no.py
	cp $(CHAP_DIR)/*.docx $(PUB_DIR)

permissions: FORCE
	cp $(PERM_DIR)/*.pdf $(PUB_DIR)

toc: $(PUB_DIR)/toc.docx

# Targets to check for missing files:
whats_missing: missing_abs missing_addrs missing_bios missing_chaps missing_keywords missing_perms

missing_abs: FORCE
	$(MISSING_PROG) $(AUTHOR_FILE) $(ABS_DIR)
	
missing_addrs: FORCE
	$(MISSING_PROG) $(AUTHOR_FILE) $(ADDR_DIR)
	
missing_bios: FORCE
	$(MISSING_PROG) $(AUTHOR_FILE) $(BIO_DIR)

missing_chaps: FORCE
	$(MISSING_PROG) $(AUTHOR_FILE) $(CHAP_DIR) docx

missing_keywords: FORCE
	$(MISSING_PROG) $(AUTHOR_FILE) $(KWORD_DIR)

missing_perms: FORCE
	$(MISSING_PROG) $(AUTHOR_FILE) $(PERM_DIR) pdf

# Proposal related targets
prop_parts: abstracts bios toc proposal

proposal: $(PROP_DIR)/prop.docx $(PROP_DIR)/palgrave.docx

$(PROP_DIR)/prop.docx: $(PROP_DIR)/prop.md
	pandoc -o $@ -f markdown -t docx $^

$(PROP_DIR)/palgrave.docx: $(PROP_DIR)/palgrave.md
	pandoc -o $@ -f markdown -t docx $^
