#ifdef XWAYLAND
#error This port must be built without XWayland
#endif
#define main dwl_main
#include "../dwl.c"
#undef main
#include <assert.h>

int
main(void)
{
    unsigned int i;
    const Key *key;
    for (i = 0; i < 9; ++i) {
        key = keybinding(MODKEY, XKB_KEY_1 + i);
        assert(key && key->func == view && key->arg.ui == (1u << i));
        key = keybinding(MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_1 + i);
        assert(key && key->func == tag && key->arg.ui == (1u << i));
        key = keybinding(MODKEY|WLR_MODIFIER_CTRL, XKB_KEY_1 + i);
        assert(key && key->func == toggleview && key->arg.ui == (1u << i));
        key = keybinding(MODKEY|WLR_MODIFIER_CTRL|WLR_MODIFIER_SHIFT, XKB_KEY_1 + i);
        assert(key && key->func == toggletag && key->arg.ui == (1u << i));
    }
    key = keybinding(MODKEY, XKB_KEY_period);
    assert(key && key->func == focusmon && key->arg.i == WLR_DIRECTION_RIGHT);
    key = keybinding(MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_period);
    assert(key && key->func == tagmon && key->arg.i == WLR_DIRECTION_RIGHT);
    key = keybinding(MODKEY, XKB_KEY_comma);
    assert(key && key->func == focusmon && key->arg.i == WLR_DIRECTION_LEFT);
    key = keybinding(MODKEY, XKB_KEY_b);
    assert(key && key->func == togglebar);
    key = keybinding(MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_Return);
    assert(key && key->func == spawn && key->arg.v == termcmd);
    assert(strcmp(termcmd[0], "foot") == 0);
    assert(strcmp(xkb_rules.layout, "latam") == 0);
    puts("Verified: tag modifiers, monitor directions, bar toggle, and native terminal binding.");
    return 0;
}
