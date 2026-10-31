execute as @e[type=text_display,tag=oszu_fd_damage_text_display] run scoreboard players add @s oszu_fd_damage_text_display_life_span 1

execute as @e[type=text_display,tag=oszu_fd_damage_text_display,scores={oszu_fd_damage_text_display_life_span=20..}] run kill @s

execute as @e[type=text_display,tag=oszu_fd_damage_text_display,scores={oszu_fd_damage_text_display_life_span=10}] run execute as @e[type=text_display] run data merge entity @s {start_interpolation:0,interpolation_duration:7,transformation:{scale:[0f,0f,0f]}}

execute as @a[scores={oszu_fd_print_off=1..}] run function oszu_fd:set_print_false

execute as @a[scores={oszu_fd_print_on=1..}] run function oszu_fd:set_print_true

execute as @a[scores={oszu_fd_compensation_for_mojang_handling_advancements_in_a_random_order=1}] at @s run function oszu_fd:modifiers/process_data