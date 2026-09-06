-- Allows the user to configure power output and total value
-- File: settings.lua

data:extend({
  {
    type = "int-setting",
    name = "vlp-power-production",
    setting_type = "startup",
    default_value = 40,
    minimum_value = 1,
    maximum_value = 250,
    order = "a-a"
  },
  {
    type = "int-setting",
    name = "vlp-lava-energy",
    setting_type = "startup",
    default_value = 180,
    minimum_value = 1,
    maximum_value = 1000,
    order = "a-b"
  },
  {
    type = "int-setting",
    name = "vlp-sluicing-stone",
    setting_type = "startup",
    default_value = 30,
    minimum_value = 0,
    maximum_value = 100,
    order = "a-c"
  },
  {
    type = "int-setting",
    name = "vlp-sluicing-output",
    setting_type = "startup",
    default_value = 240,
    minimum_value = 1,
    maximum_value = 500,
    order = "a-d"
  }
})
