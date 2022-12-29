// Include MicroPython API.
#include "py/runtime.h"
#include "bpm_filter_chain.h"

// args(minBpm, maxBpm, sampleRate, filterStrength)
STATIC mp_obj_t mp_module_init(size_t n_args, const mp_obj_t *args) {
    init(
        mp_obj_get_float_to_f(args[0]), // minBpm
        mp_obj_get_float_to_f(args[1]), // maxBpm
        mp_obj_get_int(args[2]), // sampleRate
        mp_obj_get_float_to_f(args[3]) // filterStrength
    );
    return mp_const_none;
}

STATIC mp_obj_t mp_updateFilter_chain(mp_obj_t newSample) {
    updateFilterChain(mp_obj_get_float_to_f(newSample));
    return mp_const_none;
}

STATIC mp_obj_t mp_findBestStrength() {
    strengthResult bestStrength = findBestStrength();
    mp_obj_t tuple[2] = {
        mp_obj_new_int(bestStrength.filterSize),
        mp_obj_new_float(bestStrength.strength)
    };
    return mp_obj_new_tuple(2, tuple);
}

// Define a Python reference to the function above.
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR(mp_module_init_obj, 4, mp_module_init);
STATIC MP_DEFINE_CONST_FUN_OBJ_1(updateFilterChain_obj, mp_updateFilter_chain);
STATIC MP_DEFINE_CONST_FUN_OBJ_0(findBestStrength_obj, mp_findBestStrength);


// Define all properties of the module.
// Table entries are key/value pairs of the attribute name (a string)
// and the MicroPython object reference.
// All identifiers and strings are written as MP_QSTR_xxx and will be
// optimized to word-sized integers by the build system (interned strings).
STATIC const mp_rom_map_elem_t example_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_cexample) },
    { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&mp_module_init_obj) },
    { MP_ROM_QSTR(MP_QSTR_updateFilterChain), MP_ROM_PTR(&updateFilterChain_obj) },
    { MP_ROM_QSTR(MP_QSTR_findBestStrength), MP_ROM_PTR(&findBestStrength_obj) },
};
STATIC MP_DEFINE_CONST_DICT(example_module_globals, example_module_globals_table);

// Define module object.
const mp_obj_module_t example_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&example_module_globals,
};

// Register the module to make it available in Python.
MP_REGISTER_MODULE(MP_QSTR_lfilter, example_user_cmodule);
