import java.awt.*;
import java.awt.geom.*;
import java.awt.image.BufferedImage;
import java.nio.file.*;
import javax.imageio.ImageIO;

/** Reproducible code-native UI geometry, not AI illustrations or game screenshots.
 * Run: java tools/art/QuestAtlasArt.java src/main/resources/assets/dynasty/textures/gui/quests
 */
public final class QuestAtlasArt {
    private static final String[] KEYS={"home","guard","sword","archer","talisman","head","necklace","ring","bracelet","hands","body","back","belt","charm"};
    private static final String[] TITLES={"王朝 · 山河行纪","玄武守御","游龙剑舞","逐星射艺","道门律令","头部 · 冠冕之章","项链 · 玉佩之章","戒指 · 指间之章","手镯 · 护腕之章","手部 · 握持之章","身体 · 护心之章","背部 · 披羽之章","腰带 · 系佩之章","护符 · 四卷秘藏"};
    private static final Color GOLD=new Color(212,185,127);
    private static Color accent(String kind){return switch(kind){case "guard"->new Color(113,179,157);case "sword"->new Color(118,191,211);case "archer"->GOLD;case "talisman"->new Color(183,148,214);default->new Color(148,177,159);};}
    private static Graphics2D graphics(BufferedImage img){
        Graphics2D g=img.createGraphics();
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON);
        g.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING,RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
        return g;
    }
    private static Font font(float size){
        for(String family:new String[]{"Songti SC","Noto Serif CJK SC","Serif"}){
            Font f=new Font(family,Font.PLAIN,Math.round(size));
            if(f.canDisplay('朝'))return f;
        }
        return new Font("Dialog",Font.PLAIN,Math.round(size));
    }
    private static void polygon(Graphics2D g,int points,double r,double rot){
        Path2D p=new Path2D.Double();
        for(int i=0;i<points;i++){double a=rot+i*Math.PI*2/points,x=Math.cos(a)*r,y=Math.sin(a)*r;if(i==0)p.moveTo(x,y);else p.lineTo(x,y);}
        p.closePath();g.draw(p);
    }
    private static void emblem(Graphics2D g,String kind,double scale){
        AffineTransform before=g.getTransform();g.scale(scale,scale);g.setStroke(new BasicStroke(1.4f));
        switch(kind){
            case "guard"->{polygon(g,6,100,Math.PI/6);polygon(g,6,82,Math.PI/6);for(int j=-1;j<=1;j++)for(int i=-1;i<=1;i++){g.translate(i*40,j*38);polygon(g,6,24,Math.PI/6);g.translate(-i*40,-j*38);}}
            case "sword"->{for(int i=-1;i<=1;i++){Path2D p=new Path2D.Double();p.moveTo(-110,-75+i*16);p.curveTo(105,-115+i*16,-105,100+i*16,110,75+i*16);g.draw(p);}polygon(g,4,88,0);g.drawLine(-58,58,58,-58);}
            case "archer"->{for(int j=0;j<2;j++){Path2D p=new Path2D.Double();for(int i=0;i<=5;i++){double a=-Math.PI/2+i*4*Math.PI/5,r=100-j*18,x=Math.cos(a)*r,y=Math.sin(a)*r;if(i==0)p.moveTo(x,y);else p.lineTo(x,y);}g.draw(p);}for(int i=0;i<8;i++){double a=i*Math.PI/4;g.draw(new Ellipse2D.Double(Math.cos(a)*116-3,Math.sin(a)*116-3,6,6));}}
            case "talisman"->{polygon(g,8,110,Math.PI/8);polygon(g,8,90,Math.PI/8);for(int i=0;i<8;i++){g.rotate(Math.PI/4);for(int j=0;j<3;j++){int x=64+j*6;if(((i>>j)&1)==1)g.drawLine(x,-13,x,13);else{g.drawLine(x,-13,x,-4);g.drawLine(x,4,x,13);}}}g.draw(new Ellipse2D.Double(-39,-39,78,78));g.draw(new Arc2D.Double(-20,-39,40,40,90,180,Arc2D.OPEN));g.draw(new Arc2D.Double(-20,-1,40,40,-90,180,Arc2D.OPEN));}
            default->{polygon(g,4,115,0);polygon(g,4,97,0);for(int i=0;i<4;i++){g.rotate(Math.PI/2);g.draw(new Arc2D.Double(-70,-104,140,82,0,180,Arc2D.OPEN));}g.draw(new Ellipse2D.Double(-45,-45,90,90));}
        }
        g.setTransform(before);
    }
    private static void title(Path dir,String key,String title)throws Exception{
        BufferedImage img=new BufferedImage(1024,144,BufferedImage.TYPE_INT_ARGB);Graphics2D g=graphics(img);
        g.setPaint(new GradientPaint(0,0,new Color(15,25,25,0),170,0,new Color(15,25,25,245),true));g.fillRoundRect(0,14,1024,116,18,18);
        g.setColor(accent(key));g.setStroke(new BasicStroke(2));g.drawLine(36,27,988,27);g.drawLine(36,118,988,118);
        for(int x:new int[]{36,988}){g.translate(x,72);polygon(g,4,10,0);g.translate(-x,-72);}
        g.setFont(font(title.length()>10?48:59));FontMetrics m=g.getFontMetrics();g.setColor(new Color(239,226,195));g.drawString(title,(1024-m.stringWidth(title))/2,91);
        g.dispose();ImageIO.write(img,"png",dir.resolve("title_"+key+".png").toFile());
    }
    private static void backdrop(Path dir,String key)throws Exception{
        BufferedImage img=new BufferedImage(1024,1024,BufferedImage.TYPE_INT_ARGB);Graphics2D g=graphics(img);
        g.setColor(new Color(15,26,28,180));g.fillRoundRect(8,8,1008,1008,60,60);
        Color c=accent(key);g.setColor(new Color(c.getRed(),c.getGreen(),c.getBlue(),145));g.setStroke(new BasicStroke(1.5f));
        g.drawRoundRect(22,22,980,980,38,38);g.drawRoundRect(34,34,956,956,28,28);
        g.translate(512,512);g.setColor(new Color(c.getRed(),c.getGreen(),c.getBlue(),105));emblem(g,key,3.45);
        g.setColor(new Color(c.getRed(),c.getGreen(),c.getBlue(),120));
        for(int i=0;i<4;i++){g.rotate(Math.PI/2);g.drawLine(-418,-449,-338,-449);g.drawLine(-449,-418,-449,-338);g.drawLine(-425,-425,-382,-425);g.drawLine(-425,-425,-425,-382);}
        g.dispose();ImageIO.write(img,"png",dir.resolve("backdrop_"+key+".png").toFile());
    }
    private static void card(Path dir,String key,String heading,String subtitle,String next)throws Exception{
        BufferedImage img=new BufferedImage(1024,268,BufferedImage.TYPE_INT_ARGB);Graphics2D g=graphics(img);
        g.setColor(new Color(14,32,31,246));g.fillRoundRect(8,8,1008,252,24,24);
        g.setColor(accent(key));g.setStroke(new BasicStroke(3));g.drawRoundRect(14,14,996,240,20,20);
        g.fillRect(38,46,5,171);g.setFont(font(58));g.setColor(new Color(242,225,189));g.drawString(heading,70,89);
        g.setFont(font(35));g.setColor(new Color(185,205,191));g.drawString(subtitle,70,150);
        g.setColor(new Color(146,189,171));g.drawString(next,70,209);
        g.dispose();ImageIO.write(img,"png",dir.resolve("card_"+key+".png").toFile());
    }
    public static void main(String[] args)throws Exception{
        Path out=Path.of(args[0]);Files.createDirectories(out);
        for(int i=0;i<KEYS.length;i++)title(out,KEYS[i],TITLES[i]);
        for(String key:new String[]{"home","guard","sword","archer","talisman","catalog"})backdrop(out,key);
        card(out,"stage_0","01 / 安家起步","没有据点：工具 → 照明 → 自保","点击进入主线第一章  ›");
        card(out,"stage_1","02 / 工坊已成","已有据点：罗盘 → 图纸 → 青铜","点击继续装备与出行准备  ›");
        card(out,"stage_2","03 / 维度探索","平叛之后：先备回程，再跨维度","点击进入天朝探索主线  ›");
        card(out,"stage_3","04 / 问鼎之后","击败龙帝：毕业搭配，自选玩法","点击查看毕业方向  ›");
        card(out,"guard","玄武守御 · 格挡反击","正面接击 → 抓住反击窗口","镇岳刀 / 镇关镜 / 虎贲护腕  ›");
        card(out,"sword","游龙剑舞 · 同敌三击","走位留路 → 满力连段","流云剑 / 连城剑穗 / 踏云佩  ›");
        card(out,"archer","逐星射艺 · 满蓄追星","首箭标记 → 第二箭兑现","逐星弓 / 观星坠 / 鸣弦环  ›");
        card(out,"talisman","道门律令 · 控场蓄势","可见敌人 → 站定蓄势 → 笔击","敕令笔 / 司天印 / 定风帛  ›");
        String[] volumes={"进攻与命中增益","防护机动与功能","条件触发 · 先看环境","代价取舍 · 先看负面"};
        for(int i=0;i<4;i++){
            title(out,"volume_"+i,volumes[i]);
            Files.move(out.resolve("title_volume_"+i+".png"),out.resolve("volume_"+i+".png"),StandardCopyOption.REPLACE_EXISTING);
        }
        System.out.println("Quest atlas: 32 code-native UI panels in "+out);
    }
}
