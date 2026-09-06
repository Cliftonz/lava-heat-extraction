local lava_heating_tower = table.deepcopy(data.raw["reactor"]["heating-tower"])

lava_heating_tower.name = "lava-heating-tower"
lava_heating_tower.minable = {mining_time = 0.5, result = "lava-heating-tower"}

local fluid_bizox = {
    volume = 1000,
    production_type = "input-output",
    filter = "filtered-lava",
    pipe_connections = {
        -- North ×2
        { flow_direction = "input-output", direction = defines.direction.north, position = {-1, -1} },
        { flow_direction = "input-output", direction = defines.direction.north, position = { 1, -1} },
        -- East ×2
        { flow_direction = "input-output", direction = defines.direction.east, position = { 1, -1} },
        { flow_direction = "input-output", direction = defines.direction.east, position = { 1, 1} },
        -- South ×2
        { flow_direction = "input-output", direction = defines.direction.south, position = {-1, 1} },
        { flow_direction = "input-output", direction = defines.direction.south, position = { 1, 1} },
        -- West ×2
        { flow_direction = "input-output", direction = defines.direction.west, position = {-1, -1} },
        { flow_direction = "input-output", direction = defines.direction.west, position = {-1, 1} },
    },
}

lava_heating_tower.energy_source = {
    type = "fluid",
    burns_fluid = true,
    scale_fluid_usage = true,
    effectivity = 2.5,
    fluid_box = fluid_bizox,
    maximum_temperature = 1000,
    specific_heat = settings.startup["vlp-power-production"].value .. "MJ",
    max_transfer = settings.startup["vlp-power-production"].value .. "MW",
}

lava_heating_tower.heat_buffer = data.raw["reactor"]["heating-tower"].heat_buffer

lava_heating_tower.consumption = settings.startup["vlp-power-production"].value .. "MW"

lava_heating_tower.fluid_usage_per_tick = settings.startup["vlp-lava-consumption"] and
settings.startup["vlp-lava-consumption"].value or 1

lava_heating_tower.max_temperature = 1000

lava_heating_tower.heating_tower_tint = {r = 0.6, g = 0.2, b = 0.9, a = 1.0}

lava_heating_tower.fixed_direction = false

lava_heating_tower.result_inventory_size = 1

local lava_pipe_pictures = assembler3pipepictures()

lava_heating_tower.energy_source.fluid_box.pipe_covers = pipecoverspictures()
lava_heating_tower.energy_source.fluid_box.pipe_picture = lava_pipe_pictures
for _, conn in pairs(lava_heating_tower.energy_source.fluid_box.pipe_connections) do
    conn.secondary_draw_order = -10
end
lava_heating_tower.energy_source.fluid_box.secondary_draw_order = -10

data:extend({lava_heating_tower})

-- Create the item
local lava_heating_tower_item = table.deepcopy(data.raw["item"]["heating-tower"])
lava_heating_tower_item.name = "lava-heating-tower"
lava_heating_tower_item.place_result = "lava-heating-tower"
lava_heating_tower_item.order = "b[steam-power]-d[lava-heating-tower]"

data:extend({lava_heating_tower_item})

-- Create the recipe (requires tungsten plates, pipes, and copper)
data:extend({
  {
    type = "recipe",
    name = "lava-heating-tower",
    enabled = false,
    energy_required = 10,
    ingredients = {
      {type = "item", name = "tungsten-carbide", amount = 40},
      {type = "item", name = "pipe", amount = 10},
      {type = "item", name = "copper-plate", amount = 50}
    },
    results = {{type = "item", name = "lava-heating-tower", amount = 1}}
  }
})

-- Add recipe unlock to tungsten-carbide technology
table.insert(data.raw.technology["tungsten-carbide"].effects, {
  type = "unlock-recipe",
  recipe = "lava-heating-tower"
})

-- Modify acid neutralization to produce cold steam (120°C)
if data.raw.recipe["acid-neutralisation"] then
  local acid_recipe = data.raw.recipe["acid-neutralisation"]

  -- Update the results to specify cold steam temperature
  for _, result in pairs(acid_recipe.results) do
    if result.name == "steam" or result[1] == "steam" then
      result.temperature = 125
    end
  end
end

-- Filtered lava: burnable fluid produced by sluicing raw lava in a foundry
if data.raw.fluid["lava"] then
  local filtered_lava = table.deepcopy(data.raw.fluid["lava"])
  filtered_lava.name = "filtered-lava"
  filtered_lava.fuel_value = settings.startup['vlp-lava-energy'].value .. "kJ"
  filtered_lava.order = (filtered_lava.order or "z") .. "-b[filtered]"

  data:extend({filtered_lava})

  local sluicing_results = {
    {type = "fluid", name = "filtered-lava", amount = settings.startup["vlp-sluicing-output"].value},
  }
  local stone_amount = settings.startup["vlp-sluicing-stone"].value
  if stone_amount > 0 then
    table.insert(sluicing_results, {type = "item", name = "stone", amount = stone_amount})
  end

  data:extend({
    {
      type = "recipe",
      name = "lava-sluicing",
      category = "metallurgy",
      enabled = false,
      energy_required = 4,
      ingredients = {{type = "fluid", name = "lava", amount = 500}},
      results = sluicing_results,
      main_product = "filtered-lava",
      allow_productivity = false,
      subgroup = "vulcanus-processes",
      order = "a[melting]-c[lava-sluicing]",
    }
  })

  table.insert(data.raw.technology["tungsten-carbide"].effects, {
    type = "unlock-recipe",
    recipe = "lava-sluicing"
  })
end
