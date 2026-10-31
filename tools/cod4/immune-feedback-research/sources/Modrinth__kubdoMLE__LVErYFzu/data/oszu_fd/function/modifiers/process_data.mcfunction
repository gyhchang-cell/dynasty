#store damage data in storage for macro
	scoreboard players operation temp oszu_fd_damage_delt = @s oszu_fd_damage_delt
	scoreboard players operation temp oszu_fd_damage_delt /= 10 oszu_fd_damage_delt
	scoreboard players operation temp oszu_fd_damage_delt *= 10 oszu_fd_damage_delt
	scoreboard players operation @s oszu_fd_damage_delt -= temp oszu_fd_damage_delt
	scoreboard players operation temp oszu_fd_damage_delt /= 10 oszu_fd_damage_delt
	execute store result storage minecraft:oszu_storage oszu_fd.damage_text_decimal int 1 run scoreboard players get @s oszu_fd_damage_delt
	execute store result storage minecraft:oszu_storage oszu_fd.damage_text_whole int 1 run scoreboard players get temp oszu_fd_damage_delt
	data modify storage minecraft:oszu_storage oszu_fd.damage_suffix set value ""
	data modify storage minecraft:oszu_storage oszu_fd.damage_prefix set value ""
	data modify storage minecraft:oszu_storage oszu_fd.damage_type set value ""
	data modify storage minecraft:oszu_storage oszu_fd.damage_tense set value "Delt"
	data modify storage minecraft:oszu_storage oszu_fd.entity_prefix set value ""
	
	function oszu_fd:modifiers/merge_damage_text with storage oszu_storage oszu_fd

#set default colour
	data modify storage minecraft:oszu_storage oszu_fd.colour set value FF003B
	
#modifier colours
	#fire damage
		execute if entity @s[advancements={oszu_fd:modifiers/fire_damage=true}] run data modify storage minecraft:oszu_storage oszu_fd.colour set value FF6A00

	#projectile damage
		execute if entity @s[advancements={oszu_fd:modifiers/projectile_damage=true}] run data modify storage minecraft:oszu_storage oszu_fd.damage_type set value "projectile "
		execute if entity @s[advancements={oszu_fd:modifiers/projectile_damage=true}] run data modify storage minecraft:oszu_storage oszu_fd.colour set value "FFFF00"
		execute if entity @s[advancements={oszu_fd:modifiers/projectile_damage=true}] run playsound minecraft:entity.experience_orb.pickup ambient @s ~ ~ ~ 0.25 1

	#entity player
		execute if entity @s[advancements={oszu_fd:modifiers/entity_player=true}] run data modify storage minecraft:oszu_storage oszu_fd.colour set value "A7003B"

	#entity warden
		execute if entity @s[advancements={oszu_fd:modifiers/entity_warden=true}] run data modify storage minecraft:oszu_storage oszu_fd.colour set value "024C7A"

	#entity elder_guardian
		execute if entity @s[advancements={oszu_fd:modifiers/entity_elder_guardian=true}] run data modify storage minecraft:oszu_storage oszu_fd.colour set value "33E8A5"

	#entity ender_dragon
		execute if entity @s[advancements={oszu_fd:modifiers/entity_ender_dragon=true}] run data modify storage minecraft:oszu_storage oszu_fd.colour set value "BE009F"

	#entity wither
		execute if entity @s[advancements={oszu_fd:modifiers/entity_wither=true}] run data modify storage minecraft:oszu_storage oszu_fd.colour set value "4F455B"

	#effect invisible
		execute if entity @s[advancements={oszu_fd:modifiers/effect_invisible=true}] run data modify storage minecraft:oszu_storage oszu_fd.colour set value "FFFFFF"
		execute if entity @s[advancements={oszu_fd:modifiers/effect_invisible=true}] run data modify storage minecraft:oszu_storage oszu_fd.damage_text set value " "
		execute if entity @s[advancements={oszu_fd:modifiers/effect_invisible=true}] run data modify storage minecraft:oszu_storage oszu_fd.entity_prefix set value "Invisible "
		
	#over 100 damage
		execute if entity @s[advancements={oszu_fd:modifiers/over_100_damage=true}] run data modify storage minecraft:oszu_storage oszu_fd.colour set value "842FFF"
		execute if entity @s[advancements={oszu_fd:modifiers/over_100_damage=true}] run data modify storage minecraft:oszu_storage oszu_fd.damage_text set value "100+"

	#damage blocked
		execute if entity @s[advancements={oszu_fd:modifiers/blocked_damage=true}] run data modify storage minecraft:oszu_storage oszu_fd.colour set value "D6FFFF"
		execute if entity @s[advancements={oszu_fd:modifiers/blocked_damage=true}] run data modify storage minecraft:oszu_storage oszu_fd.damage_text set value "Blocked"

					#You can add your own custom colours here, simpl go to advancements/modifiers and add a new advancement with the desired predicate, and here add a new line, like the others, targeting the advancemnt
					#and either changing the text colour, what the text says, both, or even any command you want! it is sorted in order top-down so that colour events at the bottom will always overwritecolour  events at the top

#run text/print display function
	function oszu_fd:modifiers/initiate_flaoting_text with storage oszu_storage oszu_fd

#reset componsation for mojang handling advancement events in a random order
	scoreboard players set @s oszu_fd_compensation_for_mojang_handling_advancements_in_a_random_order 0

#revoke modifeir advancements
	advancement revoke @s only oszu_fd:damage/damage_100_plus
	advancement revoke @s only oszu_fd:modifiers/blocked_damage
	advancement revoke @s only oszu_fd:modifiers/over_100_damage
	advancement revoke @s only oszu_fd:modifiers/fire_damage
	advancement revoke @s only oszu_fd:modifiers/projectile_damage
	advancement revoke @s only oszu_fd:modifiers/entity_player
	advancement revoke @s only oszu_fd:modifiers/entity_wither
	advancement revoke @s only oszu_fd:modifiers/entity_ender_dragon
	advancement revoke @s only oszu_fd:modifiers/entity_elder_guardian
	advancement revoke @s only oszu_fd:modifiers/entity_warden
	advancement revoke @s only oszu_fd:modifiers/effect_invisible
