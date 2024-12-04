export WORD_DIR = ./word_docs
export PUB_DIR = ./to_publisher
export BIO_DIR = ./bio
export ABS_DIR = ./abstract
export TMP_DIR = ./tmp
export BIN_DIR = ./bin
export PROP_DIR = ./proposal
export STRUCT_DIR = ./structure
export ARCH_NAME = AuthorityAndRebellion
export ARCH_FILE = $(PUB_DIR)/$(ARCH_NAME).zip

prod: parts github

archive: $(ARCH_FILE)

$(ARCH_FILE): parts
	zip -r $(ARCH_FILE) $(WORD_DIR)/*.docx

github:
	-git commit -a
	git push origin main

parts: abstract bio toc proposal

toc: $(WORD_DIR)/toc.docx

$(WORD_DIR)/toc.docx: toc.md
	pandoc -o $@ -f markdown -t docx toc.md

proposal: $(WORD_DIR)/prop.docx $(WORD_DIR)/palgrave.docx

$(WORD_DIR)/prop.docx: $(PROP_DIR)/prop.md
	pandoc -o $@ -f markdown -t docx $(PROP_DIR)/prop.md

$(WORD_DIR)/palgrave.docx: $(PROP_DIR)/palgrave.md
	pandoc -o $@ -f markdown -t docx $(PROP_DIR)/palgrave.md

abstract: $(WORD_DIR)/abstract.docx

$(WORD_DIR)/abstract.docx: $(TMP_DIR)/abstract.md
	pandoc -o $@ -f markdown -t docx $(TMP_DIR)/abstract.md

$(TMP_DIR)/abstract.md: $(ABS_DIR)/*.md $(STRUCT_DIR)/chap_order.txt
	$(BIN_DIR)/collect_abstract.sh

bio: $(WORD_DIR)/bio.docx

$(WORD_DIR)/bio.docx: $(TMP_DIR)/bio.md
	pandoc -o $@ -f markdown -t docx $(TMP_DIR)/bio.md

$(TMP_DIR)/bio.md: $(BIO_DIR)/*.md
	cat $^ > $@
