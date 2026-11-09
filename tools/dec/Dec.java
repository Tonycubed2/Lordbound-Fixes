import resaver.pex.*;
import java.nio.file.*;
import java.util.*;
public class Dec {
  public static void main(String[] a) throws Exception {
    Path in=Paths.get(a[0]), out=Paths.get(a[1]); int ok=0,bad=0;
    try (DirectoryStream<Path> ds=Files.newDirectoryStream(in,"*.pex")) {
      for (Path p: ds) {
        String n=p.getFileName().toString().toLowerCase().replaceAll("\\.pex$",".psc");
        try { PexFile f=PexFile.readScript(p); List<String> c=new ArrayList<>(); f.disassemble(c, AssemblyLevel.FULL); Files.write(out.resolve(n), c); ok++; }
        catch (Throwable t) { try { PexFile f=PexFile.readScript(p); List<String> c=new ArrayList<>(); f.disassemble(c, AssemblyLevel.BYTECODE); c.add(0,"; BYTECODE-LEVEL"); Files.write(out.resolve(n), c); ok++; } catch (Throwable t2) { bad++; System.err.println(n+": "+t2);} }
      }
    }
    System.out.println("ok="+ok+" bad="+bad);
  }
}
