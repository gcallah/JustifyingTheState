export WORD_DIR = ./word_docs
export PUB_DIR = ./to_publisher
export BIO_DIR = ./bios
export ABS_DIR = ./abstracts
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

parts: abstracts bios toc proposal

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
