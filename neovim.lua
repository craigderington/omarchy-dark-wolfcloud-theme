-- Dark Wolfcloud: native aether palette with ion/ember emphasis.
return {
  {
    "omacom/aether.nvim",
    branch = "v3",
    name = "aether",
    priority = 1000,
    opts = {
      styles = { comments = { italic = true }, keywords = { italic = false } },
      on_highlights = function(hl, c)
        hl.Function = { fg = c.cyan }
        hl["@function"] = { fg = c.cyan }
        hl["@function.call"] = { fg = c.cyan }
        hl.Visual = { bg = c.selection, fg = c.selection_foreground }
        hl.Search = { bg = "#493b2c", fg = "#ffe2a8" }
        hl.IncSearch = { bg = "#ffbf69", fg = "#0b1216" }
        hl.CurSearch = { bg = "#ffbf69", fg = "#0b1216" }
      end,
      colors = {
        bg = "#0b1216",
        dark_bg = "#080e12",
        darker_bg = "#05090c",
        lighter_bg = "#18262d",

        fg = "#d4e2df",
        dark_fg = "#8ba2a4",
        light_fg = "#b5cacb",
        bright_fg = "#edfaf5",
        muted = "#789095",

        red = "#f47770",
        yellow = "#f4cf8a",
        orange = "#ffad66",
        green = "#9dbfa4",
        cyan = "#71e5e8",
        blue = "#83b8ce",
        magenta = "#d78db8",
        brown = "#ae8a6b",

        bright_red = "#ff9990",
        bright_yellow = "#ffe2a8",
        bright_green = "#bce0be",
        bright_cyan = "#a6f5ef",
        bright_blue = "#abd6e7",
        bright_magenta = "#efb2d5",

        accent = "#71e5e8",
        cursor = "#edfaf5",
        foreground = "#d4e2df",
        background = "#0b1216",
        selection = "#493b2c",
        selection_foreground = "#fff0d4",
        selection_background = "#493b2c",
      },
    },
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "aether",
    },
  },
}
