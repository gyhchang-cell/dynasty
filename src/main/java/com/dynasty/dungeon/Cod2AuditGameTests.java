package com.dynasty.dungeon;

import com.dynasty.blueprint.*;
import com.dynasty.worldevent.*;
import com.google.gson.*;
import net.minecraft.gametest.framework.GameTest;
import net.minecraft.gametest.framework.GameTestHelper;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraftforge.gametest.GameTestHolder;
import net.minecraftforge.gametest.PrefixGameTestTemplate;
import net.minecraftforge.registries.ForgeRegistries;
import java.nio.file.*;
import java.util.*;

/** Opt-in native registry evidence. A definition or a passing audit never certifies full gameplay. */
@GameTestHolder("dynasty_cod2")
@PrefixGameTestTemplate(false)
public final class Cod2AuditGameTests {
    @GameTest(template="bow_ritual_test",batch="cod2_runtime_audit")
    public static void exportActualRegistryDependenciesAndAuthoredTimelines(GameTestHelper h)throws java.io.IOException{
        var gson=new GsonBuilder().setPrettyPrinting().serializeNulls().registerTypeAdapter(ResourceLocation.class,
            (JsonSerializer<ResourceLocation>)(id,type,context)->new JsonPrimitive(id.toString())).create();
        var root=new JsonObject();root.addProperty("schema",1);root.addProperty("scope","Runtime evidence only; complete gameplay and visual acceptance remain separate");
        root.add("registeredDungeons",gson.toJsonTree(List.of(DungeonDefinition.CHENSHA)));
        root.add("chenshaMissingDependencies",gson.toJsonTree(DungeonEncounters.missingChenshaDependencies(h.getLevel())));
        root.add("ecology",gson.toJsonTree(EcologyRules.ALL));root.add("missingEcologyEntities",gson.toJsonTree(EcologyRules.missingDependencies()));
        root.add("unboundEcologyRoles",gson.toJsonTree(EcologyRules.UNBOUND_SOURCE_ROLES));
        var events=new JsonArray();
        for(var definition:WorldEventDefinitions.ALL.values()){
            var row=gson.toJsonTree(definition).getAsJsonObject();row.add("missingDependencies",gson.toJsonTree(DynastyWorldEventManager.missing(h.getLevel(),definition)));
            row.addProperty("acceptance",definition.controller()==WorldEventDefinition.Controller.UNIMPLEMENTED?"UNIMPLEMENTED":"PARTIAL; full source branches not accepted");events.add(row);
        }
        root.add("events",events);
        var entities=new JsonArray();
        for(var registered:BlueprintEntities.ENTITIES.getEntries())if(registered.get().getCategory()==net.minecraft.world.entity.MobCategory.MONSTER){
            var entity=registered.get().create(h.getLevel());if(!(entity instanceof TemplateMob mob))continue;
            var row=new JsonObject();row.addProperty("id",registered.getId().toString());row.addProperty("kind",mob.kind().name());row.addProperty("profile",mob.animationProfile().name());
            row.addProperty("movementAttribute",mob.getAttributeValue(Attributes.MOVEMENT_SPEED));
            row.addProperty("geo","src/main/resources/assets/dynasty/geo/blueprint/"+mob.blueprintId()+".geo.json");
            row.addProperty("animation","src/main/resources/assets/dynasty/animations/blueprint/"+mob.blueprintId()+".animation.json");
            row.addProperty("secondaryDistance",mob.animationProfile().secondaryDistance());entities.add(row);
        }
        root.add("entities",entities);var profiles=new JsonArray();
        for(var profile:AnimationProfile.values()){
            var row=new JsonObject();row.addProperty("id",profile.name());row.addProperty("floating",profile.floating());row.addProperty("secondaryDistance",profile.secondaryDistance());
            row.add("kinds",gson.toJsonTree(Arrays.stream(TemplateMob.Kind.values()).filter(kind->AnimationProfile.forKind(kind)==profile).map(Enum::name).toList()));profiles.add(row);
        }
        root.add("animationProfiles",profiles);var skills=new ArrayList<com.dynasty.blueprint.combat.SkillDefinition>();
        skills.addAll(List.of(TemplateSkills.SWORD,TemplateSkills.SHIELD,TemplateSkills.TALISMAN,TemplateSkills.BUFF,TemplateSkills.LEAP,TemplateSkills.ROCK));skills.addAll(ArmySkills.ALL);
        root.add("serverAttackTimelines",gson.toJsonTree(skills));
        h.assertTrue(events.size()==30&&profiles.size()==11&&EcologyRules.ALL.size()==10,"Native report keeps all source catalog entries, including missing dependencies");
        for(var rule:EcologyRules.ALL)for(var member:rule.members())if(ForgeRegistries.ENTITY_TYPES.containsKey(member.mobType())){
            var type=ForgeRegistries.ENTITY_TYPES.getValue(member.mobType());
            h.assertTrue(type!=null&&!com.dynasty.DynastyBossCombat.BarHolder.class.isAssignableFrom(type.getBaseClass()),"Boss never enters natural ecology member pool: "+member.mobType());
        }
        String destination=System.getProperty("dynasty.cod2Audit.file","");
        if(!destination.isBlank()){var file=Path.of(destination);Files.createDirectories(file.getParent());Files.writeString(file,gson.toJson(root)+"\n");}
        h.succeed();
    }
    private Cod2AuditGameTests(){}
}
