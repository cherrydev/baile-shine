LFILTER_MOD_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(LFILTER_MOD_DIR)/examplemodule.c

# We can add our module folder to include paths if needed
# This is not actually needed in this example.
CFLAGS_USERMOD += -I$(LFILTER_MOD_DIR)
LFILTER_MOD_DIR := $(USERMOD_DIR)
