package com.dynasty.client;

import com.google.gson.*;
import net.minecraft.client.Minecraft;
import net.minecraft.client.Screenshot;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.ClickEvent;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.Style;
import java.io.*;
import java.lang.reflect.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.*;

/** Native widget/parser and Screen input probes. Only the isolated QA source set loads this. */
public final class QuestJourneyUiQa {
    static JsonObject plan;
    static int phase,index;
    static boolean ready,recording;
    static final Set<Object> drawnImages=Collections.newSetFromMap(new IdentityHashMap<>());
    static final Set<String> drawnEdges=new LinkedHashSet<>();
    static final List<String> evidence=new ArrayList<>();
    static final Set<String> capturedFigures=new HashSet<>();
    static int inlineChecks,linkChecks,cardChecks,hoverChecks;

    static Object call(Object o,String name,Class<?>[] types,Object... args)throws Exception {
        // A public member on a private nested widget still needs accessible=true.
        Method m=o.getClass().getMethod(name,types);m.setAccessible(true);return m.invoke(o,args);
    }
    static Object call(Object o,String name)throws Exception{return call(o,name,new Class<?>[0]);}
    static Object field(Object o,String name)throws Exception {
        for(Class<?> c=o.getClass();c!=null;c=c.getSuperclass()){
            try{Field f=c.getDeclaredField(name);f.setAccessible(true);return f.get(o);}
            catch(NoSuchFieldException ignored){}
        }
        throw new NoSuchFieldException(o.getClass()+"."+name);
    }
    static long id(Object o)throws Exception{return ((Number)call(o,"getId")).longValue();}
    static long hex(JsonObject r,String key){return Long.parseUnsignedLong(r.get(key).getAsString(),16);}
    static String hex(long id){return String.format("%016x",id);}
    static Object screen(Object file)throws Exception{return ((Optional<?>)call(file,"getQuestScreen")).orElseThrow();}
    static Object view(Object file)throws Exception{return field(screen(file),"viewQuestPanel");}
    static void open(long id)throws Exception {
        QuestIntegrationQa.type("client.ClientQuestFile").getMethod("openBookToQuestObject",long.class).invoke(null,id);
    }
    static List<Object> descendants(Object panel)throws Exception {
        List<Object> all=new ArrayList<>();
        if(!Class.forName("dev.ftb.mods.ftblibrary.ui.Panel").isInstance(panel))return all;
        for(Object child:(Collection<?>)call(panel,"getWidgets")){all.add(child);all.addAll(descendants(child));}
        return all;
    }
    record Box(int x,int y,int w,int h) {
        int right(){return x+w;} int bottom(){return y+h;}
        boolean contains(int px,int py){return px>=x&&py>=y&&px<right()&&py<bottom();}
    }
    static Box box(Object widget)throws Exception {
        int x=((Number)call(widget,"getX")).intValue(),y=((Number)call(widget,"getY")).intValue();
        // Panel removes its draw/update offsets afterwards. Restore ancestor scroll
        // in hit coordinates, using the same truncation as the native setOffset().
        for(Object p=field(widget,"parent");p!=null;p=field(p,"parent")){
            x+=(int)-((Number)call(p,"getScrollX")).doubleValue();
            y+=(int)-((Number)call(p,"getScrollY")).doubleValue();
        }
        return new Box(x,y,((Number)call(widget,"getWidth")).intValue(),((Number)call(widget,"getHeight")).intValue());
    }
    static void render(Minecraft mc,int x,int y)throws Exception {
        QuestIntegrationQa.check(mc.gameDirectory.getCanonicalPath().endsWith("/build/quest-journey-client-v3"),"Native UI input stays in isolated QA directory");
        if(mc.screen==null)throw new AssertionError("No native screen");
        drawnImages.clear();drawnEdges.clear();recording=true;
        try{
            mc.getMainRenderTarget().bindWrite(true);
            GuiGraphics graphics=new GuiGraphics(mc,mc.renderBuffers().bufferSource());
            // Native render consumes a virtual GUI pointer; no GLFW cursor or OS input.
            mc.screen.render(graphics,x,y,0.0f);graphics.flush();
        }finally{recording=false;}
    }
    static void capture(Minecraft mc,String name)throws Exception {
        try(var pixels=Screenshot.takeScreenshot(mc.getMainRenderTarget())){pixels.writeToFile(QuestIntegrationQa.OUT.resolve(name+".png"));}
    }
    static int[] reveal(Minecraft mc,Object file,Object widget,boolean fullImage)throws Exception {
        Object content=field(view(file),"panelContent");
        for(int attempt=0;attempt<40;attempt++){
            Box b=box(widget),v=box(content);
            int x=b.x+2,y=b.y+4;
            boolean visible=fullImage ? b.y>=v.y&&b.bottom()<=v.bottom()&&b.x>=v.x&&b.right()<=v.right() : v.contains(x,y);
            if(visible)return new int[]{x,y};
            int px=v.x+v.w/2,py=v.y+v.h/2;render(mc,px,py);
            boolean moved=mc.screen.mouseScrolled(px,py,b.y<v.y?1.0:-1.0);
            if(!moved)throw new AssertionError("Cannot reveal native content with wheel: "+widget.getClass());
        }
        throw new AssertionError("Native wheel did not reveal content");
    }
    static Object questButton(Object panel,long expected)throws Exception {
        for(Object widget:(Collection<?>)call(panel,"getWidgets")){
            if(widget.getClass().getName().endsWith(".QuestButton")&&id(field(widget,"quest"))==expected)return widget;
        }
        throw new AssertionError("Missing native quest button "+hex(expected));
    }
    static void click(Minecraft mc,int x,int y)throws Exception {
        render(mc,x,y);
        boolean handled=mc.screen.mouseClicked(x,y,0);
        mc.screen.mouseReleased(x,y,0);
        QuestIntegrationQa.check(handled,"Native Screen left-click handled at "+x+","+y);
        render(mc,4,4);
    }
    public static void recordImage(Object widget){if(recording)drawnImages.add(widget);}
    public static void recordConnection(Object from,Object to){
        if(!recording)return;
        try{drawnEdges.add(hex(id(field(from,"quest")))+">"+hex(id(field(to,"quest"))));}
        catch(Exception ex){throw new IllegalStateException("Native render probe failed",ex);}
    }

    static boolean tick(Minecraft mc,Object file)throws Exception {
        if(plan==null){
            try(InputStream stream=QuestJourneyUiQa.class.getResourceAsStream("/dynasty-quest-qa-plan.json")){
                if(stream==null)throw new AssertionError("Missing QA resource plan");
                plan=JsonParser.parseReader(new InputStreamReader(stream,StandardCharsets.UTF_8)).getAsJsonObject();
            }
        }
        String[] phases={"inline","links","cards","hover"};
        if(phase>=phases.length){
            QuestIntegrationQa.check(inlineChecks==plan.getAsJsonArray("inline").size(),"All "+inlineChecks+" inline placements parsed into and drawn by native FTB image widgets");
            QuestIntegrationQa.check(capturedFigures.size()==26,"Rendered native inline screenshots cover all 26 operation figures");
            QuestIntegrationQa.check(linkChecks==plan.getAsJsonArray("links").size(),"All "+linkChecks+" text jumps accepted through native Screen input");
            QuestIntegrationQa.check(cardChecks==plan.getAsJsonArray("cards").size(),"All "+cardChecks+" map-card and charm-label clicks reached exact targets");
            QuestIntegrationQa.check(hoverChecks==plan.getAsJsonArray("hover").size(),"All "+hoverChecks+" sampled hidden prerequisite edges rendered only on hover");
            Files.write(QuestIntegrationQa.OUT.resolve("native-ui-input.txt"),evidence);return true;
        }
        JsonArray rows=plan.getAsJsonArray(phases[phase]);
        if(index>=rows.size()){phase++;index=0;ready=false;return false;}
        JsonObject row=rows.get(index).getAsJsonObject();
        if(!ready){
            open(hex(row,phase==2?"chapter":"quest"));
            Object s=screen(file);call(field(s,"chapterPanel"),"setExpanded",new Class<?>[]{boolean.class},false);
            render(mc,4,4);
            if(phase==2){
                Object panel=field(s,"questPanel");
                call(panel,"scrollTo",new Class<?>[]{double.class,double.class},row.get("x").getAsDouble(),row.get("y").getAsDouble());
            }else if(phase==3){
                Object quest=call(file,"getQuest",new Class<?>[]{long.class},hex(row,"quest"));
                call(s,"closeQuest");
                int zoom=((Number)call(s,"getZoom")).intValue();
                call(s,"addZoom",new Class<?>[]{double.class},(8-zoom)/4.0);
                render(mc,4,4);
                double minX=((Number)call(quest,"getX")).doubleValue(),maxX=minX;
                double minY=((Number)call(quest,"getY")).doubleValue(),maxY=minY;
                for(JsonElement dependency:row.getAsJsonArray("deps")){
                    Object parent=call(file,"getQuest",new Class<?>[]{long.class},Long.parseUnsignedLong(dependency.getAsString(),16));
                    double x=((Number)call(parent,"getX")).doubleValue(),y=((Number)call(parent,"getY")).doubleValue();
                    minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);
                }
                call(field(s,"questPanel"),"scrollTo",new Class<?>[]{double.class,double.class},
                    (minX+maxX)/2,(minY+maxY)/2);
            }
            ready=true;return false;
        }
        render(mc,4,4);
        if(phase==0)inline(mc,file,row);
        else if(phase==1)link(mc,file,row);
        else if(phase==2)card(mc,file,row);
        else hover(mc,file,row);
        ready=false;index++;return false;
    }
    static void inline(Minecraft mc,Object file,JsonObject row)throws Exception {
        String image=row.get("image").getAsString();Object widget=null;
        for(Object candidate:descendants(field(view(file),"panelText"))){
            if(candidate.getClass().getName().endsWith(".ImageComponentWidget")&&((Number)field(candidate,"index")).intValue()==row.get("line").getAsInt()){
                widget=candidate;break;
            }
        }
        if(widget==null)throw new AssertionError("FTB did not parse inline image: "+row);
        Object component=call(widget,"getComponent"),icon=field(component,"image");
        String actual=String.valueOf(Class.forName("dev.ftb.mods.ftblibrary.config.ImageResourceConfig")
            .getMethod("getResourceLocation",Class.forName("dev.ftb.mods.ftblibrary.icon.Icon")).invoke(null,icon));
        QuestIntegrationQa.check(image.equals(actual),"Native image parser resolves exact asset "+image);
        QuestIntegrationQa.check(((Number)field(component,"width")).intValue()==220&&((Number)field(component,"height")).intValue()==110,"Native inline image dimensions are 220x110");
        QuestIntegrationQa.check((Boolean)field(component,"fit"),"Native image parser enables fitting to quest body width");
        int[] p=reveal(mc,file,widget,true);render(mc,p[0],p[1]);
        QuestIntegrationQa.check(drawnImages.contains(widget),"Native visible ImageComponentWidget.draw called for "+hex(hex(row,"quest"))+":"+row.get("line"));
        if(capturedFigures.add(image))capture(mc,"inline-"+image.substring(image.lastIndexOf('/')+1,image.length()-4));
        evidence.add("INLINE "+row+" native parser/widget/draw; screenshot per unique figure");inlineChecks++;
    }
    static void link(Minecraft mc,Object file,JsonObject row)throws Exception {
        Object target=null;
        for(Object widget:descendants(field(view(file),"panelText"))){
            if(!widget.getClass().getName().endsWith("$QuestDescriptionField"))continue;
            Component text=(Component)field(widget,"component");
            boolean hasJump=text.visit((style,value)->{
                ClickEvent event=style.getClickEvent();
                return event!=null&&event.getAction()==ClickEvent.Action.CHANGE_PAGE&&event.getValue().equals(row.get("target").getAsString())
                    ? Optional.of(true) : Optional.<Boolean>empty();
            },Style.EMPTY).orElse(false);
            if(hasJump){target=widget;break;}
        }
        if(target==null)throw new AssertionError("Missing parsed native jump "+row);
        int[] p=reveal(mc,file,target,false);click(mc,p[0],p[1]);
        Object viewed=call(view(file),"getViewedQuest");
        QuestIntegrationQa.check(viewed!=null&&id(viewed)==hex(row,"target"),"Native text click reaches exact quest "+row.get("target"));
        capture(mc,"jump-"+index);evidence.add("TEXT_CLICK "+row);linkChecks++;
    }
    static void card(Minecraft mc,Object file,JsonObject row)throws Exception {
        Object s=screen(file),panel=field(s,"questPanel"),target=null;
        for(Object widget:(Collection<?>)call(panel,"getWidgets")){
            if(!widget.getClass().getName().endsWith(".ChapterImageButton"))continue;
            Object image=field(widget,"chapterImage");
            if(call(image,"getClick").equals("#"+row.get("target").getAsString())){target=widget;break;}
        }
        if(target==null)throw new AssertionError("Missing native clickable image "+row);
        Box b=box(target),v=box(panel);int x=b.x+b.w/2,y=b.y+b.h/2;
        QuestIntegrationQa.check(v.contains(x,y),"Native map label center is visible");click(mc,x,y);
        s=screen(file);
        if(row.get("target_type").getAsString().equals("chapter")){
            QuestIntegrationQa.check(id(field(s,"selectedChapter"))==hex(row,"target"),"Native home card selects exact chapter "+row.get("target"));
        }else{
            Object viewed=call(view(file),"getViewedQuest");
            QuestIntegrationQa.check(viewed!=null&&id(viewed)==hex(row,"target"),"Native charm label opens exact quest "+row.get("target"));
        }
        capture(mc,"card-"+index);evidence.add("CARD_CLICK "+row);cardChecks++;
    }
    static void hover(Minecraft mc,Object file,JsonObject row)throws Exception {
        Object s=screen(file),panel=field(s,"questPanel"),button=questButton(panel,hex(row,"quest"));
        Object quest=field(button,"quest");
        QuestIntegrationQa.check((Boolean)call(quest,"shouldHideDependencyLines"),"Native sampled quest hides default dependency lines");
        Box b=box(button),v=box(panel);int x=b.x+b.w/2,y=b.y+b.h/2;
        QuestIntegrationQa.check(v.contains(x,y),"Native hover target center is visible");
        String prefix=row.get("quest").getAsString()+">";
        render(mc,4,4);
        QuestIntegrationQa.check(!(Boolean)call(button,"isMouseOver")&&drawnEdges.stream().noneMatch(e->e.startsWith(prefix)),"Native renderer emits no sampled incoming edges without hover");
        capture(mc,"hover-"+index+"-before");render(mc,x,y);
        QuestIntegrationQa.check((Boolean)call(button,"isMouseOver"),"Native render updates hovered quest button");
        for(JsonElement dependency:row.getAsJsonArray("deps")){
            QuestIntegrationQa.check(drawnEdges.contains(prefix+dependency.getAsString()),"Native renderer draws hovered prerequisite "+prefix+dependency.getAsString());
        }
        capture(mc,"hover-"+index+"-during");render(mc,4,4);
        QuestIntegrationQa.check(drawnEdges.stream().noneMatch(e->e.startsWith(prefix)),"Native sampled incoming edges disappear after pointer leaves");
        capture(mc,"hover-"+index+"-after");evidence.add("HOVER_RENDER "+row+" before=0; during=exact-deps; after=0");hoverChecks++;
    }
}
