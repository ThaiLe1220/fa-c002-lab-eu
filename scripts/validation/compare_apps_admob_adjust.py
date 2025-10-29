#!/usr/bin/env python3
"""
Compare Apps Between AdMob and Adjust Historical Data

Checks:
1. Which apps are in both sources (will join successfully)
2. Which apps are only in AdMob (no Adjust attribution data)
3. Which apps are only in Adjust (no AdMob revenue data)
4. Row counts per app to understand data volume
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

ADMOB_FILE = project_root / "data" / "historical" / "admob_historical.csv"
ADJUST_FILE = project_root / "data" / "historical" / "adjust_historical.csv"


def load_data():
    """Load both CSV files."""

    console.print("[cyan]Loading data...[/cyan]")

    try:
        admob_df = pd.read_csv(ADMOB_FILE)
        console.print(f"[green]✓ AdMob: {len(admob_df):,} rows[/green]")
    except FileNotFoundError:
        console.print(f"[red]✗ AdMob file not found: {ADMOB_FILE}[/red]")
        return None, None

    try:
        adjust_df = pd.read_csv(ADJUST_FILE)
        console.print(f"[green]✓ Adjust: {len(adjust_df):,} rows[/green]")
    except FileNotFoundError:
        console.print(f"[red]✗ Adjust file not found: {ADJUST_FILE}[/red]")
        return None, None

    return admob_df, adjust_df


def analyze_apps(admob_df, adjust_df):
    """Compare app lists between sources."""

    console.print("\n[bold cyan]═══ APP COMPARISON ═══[/bold cyan]\n")

    # Get unique apps from each source
    admob_store_ids = set(admob_df["app_store_id"].unique())
    adjust_store_ids = set(adjust_df["store_id"].unique())

    console.print(f"[cyan]Unique apps:[/cyan]")
    console.print(f"  AdMob (app_store_id):  {len(admob_store_ids)}")
    console.print(f"  Adjust (store_id):     {len(adjust_store_ids)}")

    # Match by package ID (store_id)
    console.print(f"\n[bold]Matching Strategy:[/bold]")
    console.print(f"  AdMob 'app_store_id' → Adjust 'store_id' (package IDs)")
    console.print(f"  Direct match using package identifiers")

    # Find matches (exact match on package ID)
    admob_apps_lower = {
        str(app).lower(): app for app in admob_store_ids if app and str(app) != "nan"
    }
    adjust_apps_lower = {
        str(app).lower(): app for app in adjust_store_ids if app and str(app) != "nan"
    }

    matched_apps = set(admob_apps_lower.keys()) & set(adjust_apps_lower.keys())
    admob_only = set(admob_apps_lower.keys()) - set(adjust_apps_lower.keys())
    adjust_only = set(adjust_apps_lower.keys()) - set(admob_apps_lower.keys())

    console.print(
        f"\n[bold green]✓ Apps in BOTH sources: {len(matched_apps)}[/bold green]"
    )
    console.print(f"[yellow]⚠ Apps only in AdMob: {len(admob_only)}[/yellow]")
    console.print(f"[yellow]⚠ Apps only in Adjust: {len(adjust_only)}[/yellow]")

    # Show matched apps with row counts
    if matched_apps:
        console.print(
            f"\n[bold cyan]Apps in Both Sources (Will Join Successfully):[/bold cyan]"
        )

        match_table = Table(title=f"Matched Apps ({len(matched_apps)})")
        match_table.add_column("App Store ID", style="cyan", overflow="fold")
        match_table.add_column("AdMob Name", style="green", overflow="fold")
        match_table.add_column("Adjust Name", style="yellow", overflow="fold")
        match_table.add_column("AdMob Rows", justify="right", style="dim")
        match_table.add_column("Adjust Rows", justify="right", style="dim")

        for app_lower in sorted(matched_apps):
            admob_store_id = admob_apps_lower[app_lower]
            adjust_store_id = adjust_apps_lower[app_lower]

            admob_rows = admob_df[admob_df["app_store_id"] == admob_store_id]
            adjust_rows = adjust_df[adjust_df["store_id"] == adjust_store_id]

            admob_name = (
                admob_rows["app_name"].iloc[0] if len(admob_rows) > 0 else "N/A"
            )
            adjust_name = adjust_rows["app"].iloc[0] if len(adjust_rows) > 0 else "N/A"

            admob_count = len(admob_rows)
            adjust_count = len(adjust_rows)

            match_table.add_row(
                admob_store_id,
                admob_name,
                adjust_name,
                f"{admob_count:,}",
                f"{adjust_count:,}",
            )

        console.print(match_table)

    # Show AdMob-only apps
    if admob_only:
        console.print(f"\n[yellow]Apps Only in AdMob (No Attribution Data):[/yellow]")

        admob_only_table = Table(title=f"AdMob Only ({len(admob_only)})")
        admob_only_table.add_column("App Store ID", style="cyan", overflow="fold")
        admob_only_table.add_column("App Name", style="yellow", overflow="fold")
        admob_only_table.add_column("Rows", justify="right")

        for app_lower in sorted(admob_only):  # Show ALL
            admob_store_id = admob_apps_lower[app_lower]
            admob_rows = admob_df[admob_df["app_store_id"] == admob_store_id]
            admob_name = (
                admob_rows["app_name"].iloc[0] if len(admob_rows) > 0 else "N/A"
            )
            count = len(admob_rows)
            admob_only_table.add_row(admob_store_id, admob_name, f"{count:,}")

        console.print(admob_only_table)

    # Show Adjust-only apps
    if adjust_only:
        console.print(f"\n[yellow]Apps Only in Adjust (No Revenue Data):[/yellow]")

        adjust_only_table = Table(title=f"Adjust Only ({len(adjust_only)})")
        adjust_only_table.add_column("App Name", style="yellow")
        adjust_only_table.add_column("Store ID", style="cyan")
        adjust_only_table.add_column("Rows", justify="right")

        for app_lower in sorted(adjust_only):  # Show ALL
            adjust_store_id = adjust_apps_lower[app_lower]
            adjust_rows = adjust_df[adjust_df["store_id"] == adjust_store_id]
            app_name = adjust_rows["app"].iloc[0] if len(adjust_rows) > 0 else "N/A"
            count = len(adjust_rows)
            adjust_only_table.add_row(app_name[:40], adjust_store_id[:40], f"{count:,}")

        console.print(adjust_only_table)

    return matched_apps, admob_only, adjust_only


def analyze_join_potential(admob_df, adjust_df):
    """Analyze how well data will join."""

    console.print(f"\n[bold cyan]═══ JOIN ANALYSIS ═══[/bold cyan]\n")

    # Count rows by date to see data coverage
    admob_by_date = admob_df.groupby("date").size()
    adjust_by_date = adjust_df.groupby("day").size()

    console.print(f"[cyan]Date Coverage:[/cyan]")
    console.print(
        f"  AdMob dates:  {admob_df['date'].min()} to {admob_df['date'].max()}"
    )
    console.print(
        f"  Adjust dates: {adjust_df['day'].min()} to {adjust_df['day'].max()}"
    )

    # Show sample join keys
    console.print(f"\n[bold]Sample Join Keys:[/bold]")
    console.print(f"\n[green]AdMob (first 3 rows):[/green]")
    console.print(
        admob_df[["date", "app_store_id", "country_code"]]
        .head(3)
        .to_string(index=False)
    )

    console.print(f"\n[yellow]Adjust (first 3 rows):[/yellow]")
    console.print(
        adjust_df[["day", "app", "store_id", "country"]].head(3).to_string(index=False)
    )

    # Country code comparison (filter out NaN)
    admob_countries = set(admob_df["country_code"].dropna().unique())
    adjust_countries = set(adjust_df["country_code"].dropna().unique())

    # Convert to list and filter out non-string values, normalize to uppercase for comparison
    admob_countries_list = sorted(
        [c.upper() for c in admob_countries if isinstance(c, str) and c != "nan"]
    )
    adjust_countries_list = sorted(
        [c.upper() for c in adjust_countries if isinstance(c, str) and c != "nan"]
    )

    # Find matches and mismatches (case-insensitive)
    matched_countries = sorted(set(admob_countries_list) & set(adjust_countries_list))
    admob_only_countries = sorted(
        set(admob_countries_list) - set(adjust_countries_list)
    )
    adjust_only_countries = sorted(
        set(adjust_countries_list) - set(admob_countries_list)
    )

    console.print(f"\n[cyan]Country Code Comparison:[/cyan]")
    console.print(f"  AdMob:  {len(admob_countries_list)} unique (ISO codes)")
    console.print(f"  Adjust: {len(adjust_countries_list)} unique (ISO codes)")
    console.print(f"  [green]✓ Matched: {len(matched_countries)}[/green]")
    console.print(f"  [yellow]⚠ AdMob only: {len(admob_only_countries)}[/yellow]")
    console.print(f"  [yellow]⚠ Adjust only: {len(adjust_only_countries)}[/yellow]")

    # Print matched countries
    console.print(
        f"\n[bold green]✓ Matched Country Codes ({len(matched_countries)}):[/bold green]"
    )
    console.print(", ".join(matched_countries))

    # Print AdMob-only countries
    if admob_only_countries:
        console.print(
            f"\n[bold yellow]⚠ AdMob Only Country Codes ({len(admob_only_countries)}):[/bold yellow]"
        )
        console.print(", ".join(admob_only_countries))

    # Print Adjust-only countries
    if adjust_only_countries:
        console.print(
            f"\n[bold yellow]⚠ Adjust Only Country Codes ({len(adjust_only_countries)}):[/bold yellow]"
        )
        console.print(", ".join(adjust_only_countries))


def main():
    """Run app comparison analysis."""

    console.print(
        Panel.fit(
            "[bold cyan]App Comparison: AdMob vs Adjust[/bold cyan]\n"
            "Analyzing which apps are in both sources",
            title="Data Analysis",
        )
    )

    # Load data
    admob_df, adjust_df = load_data()

    if admob_df is None or adjust_df is None:
        console.print("[red]Cannot proceed without both data files[/red]")
        return 1

    # Analyze apps
    matched, admob_only, adjust_only = analyze_apps(admob_df, adjust_df)

    # Analyze join potential
    analyze_join_potential(admob_df, adjust_df)

    # Summary
    total_apps = len(matched) + len(admob_only) + len(adjust_only)
    match_pct = (len(matched) / total_apps * 100) if total_apps > 0 else 0

    console.print(
        Panel.fit(
            f"[bold cyan]Summary[/bold cyan]\n\n"
            f"Total unique apps: {total_apps}\n"
            f"[green]✓ Matched (both sources): {len(matched)} ({match_pct:.1f}%)[/green]\n"
            f"[yellow]⚠ AdMob only: {len(admob_only)}[/yellow]\n"
            f"[yellow]⚠ Adjust only: {len(adjust_only)}[/yellow]\n\n"
            f"[bold]Next Steps:[/bold]\n"
            f"1. Map app names in dbt intermediate layer\n"
            f"2. Create country code mapping (ISO ↔ Full Name)\n"
            f"3. Use LEFT JOIN from AdMob (keep all revenue)",
            title="Result",
        )
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())


# ═══════════════════════════════════════════════════════════════════
# SAVED OUTPUT (2025-10-27) - Last run on historical data
# ═══════════════════════════════════════════════════════════════════
#
# ╭───────────── Data Analysis ──────────────╮
# │ App Comparison: AdMob vs Adjust          │
# │ Analyzing which apps are in both sources │
# ╰──────────────────────────────────────────╯
# Loading data...
# ✓ AdMob: 25,604 rows
# ✓ Adjust: 25,777 rows
#
# ═══ APP COMPARISON ═══
#
# Unique apps:
#   AdMob (app_store_id):  53
#   Adjust (store_id):     42
#
# Matching Strategy:
#   AdMob 'app_store_id' → Adjust 'store_id' (package IDs)
#   Direct match using package identifiers
#
# ✓ Apps in BOTH sources: 38
# ⚠ Apps only in AdMob: 14
# ⚠ Apps only in Adjust: 4
#
# Apps in Both Sources (Will Join Successfully):
#                                Matched Apps (38)
# ┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
# ┃ App Store ID   ┃ AdMob Name     ┃ Adjust Name     ┃ AdMob Rows ┃ Adjust Rows ┃
# ┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
# │ 6563144550     │ AI Photo       │ iOS Photo       │        283 │         327 │
# │                │ Enhancer       │ Enhancer        │            │             │
# │                │ Unblur Image   │                 │            │             │
# │ 6739825897     │ AI Video       │ iOS AI Video    │         41 │          46 │
# │                │ Generator -    │ Generator -     │            │             │
# │                │ Sorix AI       │ Text2Video      │            │             │
# │ 6743065843     │ Authenticator  │ iOS             │         18 │          17 │
# │                │ App 2FA        │ Authenticator   │            │             │
# │                │ Security       │                 │            │             │
# │ ai.assistance. │ Currency       │ AI Financial    │        124 │         126 │
# │ financial.tool │ Convert Loan   │ Tools           │            │             │
# │ s              │ Tracker        │                 │            │             │
# │ ai.fusion.char │ AI Mix, Merge  │ AI Fusion       │        886 │       1,042 │
# │ acter.merge    │ Animal Fun     │                 │            │             │
# │                │ Games          │                 │            │             │
# │ ai.video.gener │ AI GPT         │ AI GPT          │      1,403 │       1,630 │
# │ ator.text.vide │ Generator-Text │ Generator-Text  │            │             │
# │ o              │ to Video       │ to Video        │            │             │
# │ airhorn.prank. │ Air Horn       │ Air Horn Prank: │      1,339 │       1,485 │
# │ funnyprank.sou │ Prank: Funny   │ Funny Sounds    │            │             │
# │ nd             │ Sounds         │                 │            │             │
# │ authenticator. │ Authenticator: │ Authenticator   │        757 │         801 │
# │ two.step.authe │ Password & 2FA │                 │            │             │
# │ ntication      │                │                 │            │             │
# │ autoclick.auto │ Auto Clicker - │ Auto Clicker    │        173 │         176 │
# │ matictap.click │ Auto Tapper    │                 │            │             │
# │ er             │ Pro            │                 │            │             │
# │ com.blockpuzzl │ Block Puzzle   │ Block Puzzle    │        810 │         836 │
# │ e.gameblock    │                │                 │            │             │
# │ com.bloodsugar │ Blood          │ Diabetes App -  │        557 │         406 │
# │ .diabetesapp   │ Pressure:      │ Blood Sugar     │            │             │
# │                │ Health Tracker │                 │            │             │
# │ com.chatbotai. │ AI Chatbot: AI │ Chat AI Bot:    │      1,224 │       1,267 │
# │ chatwithai     │ smart          │ Chatbot         │            │             │
# │                │ assistant      │ Assistant       │            │             │
# │ com.filerecove │ Photo Recover  │ File Recovery:  │         38 │          40 │
# │ ry.photorecove │ & File         │ Photo Recovery  │            │             │
# │ ry.allrecover  │ Recovery       │                 │            │             │
# │ com.flashlight │ Led Light & 3D │ Flashlight -    │        891 │         866 │
# │ .flashlightled │ Wallpaper App  │ SOS Torch Light │            │             │
# │ com.game.match │ 3D Match       │ Match Triple 3D │        805 │         845 │
# │ triple3d       │ Triple         │                 │            │             │
# │ com.musicplaye │ Musi: Play     │ Music Player,   │      1,458 │       1,492 │
# │ r.music.app    │ Music Files    │ Play MP3        │            │             │
# │                │ Offline        │ Offline         │            │             │
# │ com.photo.enha │ AI Photo       │ AI Photo        │      1,274 │       1,453 │
# │ ncer.image     │ Enhancer &     │ Enhancer Unblur │            │             │
# │                │ Generator      │ Photo           │            │             │
# │ com.qrcodescan │ QR & Barcode   │ QR Code Reader  │        502 │         474 │
# │ ner.barcodesca │ Quick          │ - QR Scanner    │            │             │
# │ nner.scannerap │ Generator      │                 │            │             │
# │ p              │                │                 │            │             │
# │ com.step.count │ Step Counter - │ Step Counter    │        403 │         311 │
# │ er.stepcounter │ Pedometer      │                 │            │             │
# │                │ Track          │                 │            │             │
# │ com.voicerecor │ Voice          │ Voice Recorder  │        819 │         953 │
# │ der.recorderap │ Recorder,      │ : Voice Memos   │            │             │
# │ p              │ Sound Changer  │                 │            │             │
# │ currency.conve │ Currency       │ Currency        │        373 │         359 │
# │ rter.exchange  │ Converter -    │ Exchange        │            │             │
# │                │ XExchange      │                 │            │             │
# │ dont.touch.ant │ AntiTheft      │ Dont Touch My   │        763 │         632 │
# │ itheft.myphone │ Hands Off My   │ Phone           │            │             │
# │                │ Phone          │                 │            │             │
# │ emicalculator. │ EMI Calculator │ EMI Calculator  │        609 │       1,036 │
# │ finance.tool   │                │                 │            │             │
# │ emoji.merge.di │ Emoji Merge:   │ Emoji Kitchen:  │        839 │       1,044 │
# │ y.mixer        │ Sticker Maker  │ DIY Merge Icon  │            │             │
# │                │ App            │                 │            │             │
# │ expense.tracke │ Money Manager  │ Money Manager   │        317 │         308 │
# │ r.budget.manag │ & Loan Planner │                 │            │             │
# │ er             │                │                 │            │             │
# │ fantasy.rolepl │ AI Chat        │ Fantasy Chat    │        687 │         965 │
# │ ay.chat        │ Fantasia       │                 │            │             │
# │                │ Character      │                 │            │             │
# │ fluidwallpaper │ Magic Fluid-4D │ Magic Fluid     │         72 │          72 │
# │ .livewallpaper │ live           │                 │            │             │
# │ .simulation    │ Wallpapers     │                 │            │             │
# │ fruitmerge.wat │ Fruit Merge -  │ Watermeow       │         17 │          16 │
# │ ermelon.waterm │ Watermelon     │                 │            │             │
# │ eow            │ Game           │                 │            │             │
# │ hairclipper.pr │ Funny Phone    │ Haircut Prank   │        760 │         964 │
# │ ank.funnyprank │ Prank Sound    │ Clipper Sounds  │            │             │
# │ .sound         │                │                 │            │             │
# │ live.satellite │ Satellite View │ Live Satellite  │        373 │         711 │
# │ .view.earth    │ Map Air        │                 │            │             │
# │                │ Quality        │                 │            │             │
# │ loan.personal. │ EMI Calculator │ Personal Loan   │        502 │         496 │
# │ quickloan      │ - Loan Planner │                 │            │             │
# │ loancompare.em │ EMI Calculator │ Loan Compare    │        110 │         110 │
# │ i.calculator   │ - Loan Compare │                 │            │             │
# │ saving.tracker │ Smart Expense  │ Expenses        │         27 │          23 │
# │ .expense.plann │ & Budget       │ Tracker         │            │             │
# │ er             │ Tracker        │                 │            │             │
# │ spinthewheel.d │ Spin the Wheel │ Spin The Wheel  │         89 │          80 │
# │ ecider.roulett │ Random Game    │                 │            │             │
# │ e              │                │                 │            │             │
# │ text.to.video. │ AI Animal Love │ Text2Pet        │      1,131 │       1,411 │
# │ aivideo.genera │ Video          │                 │            │             │
# │ tor            │ Generator      │                 │            │             │
# │ time.bomb.simu │ Time Bomb -    │ Time Bomb -     │        644 │         901 │
# │ lator.pranksou │ Prank Gun      │ Prank Gun       │            │             │
# │ nds            │ Sounds         │ Sounds          │            │             │
# │ transparent.sc │ Wallpaper 4K:  │ Transparent     │        163 │         157 │
# │ reen.livewallp │ HD BackGround  │ Live Wallpaper  │            │             │
# │ aper.wallpaper │                │ 8K              │            │             │
# │ hd             │                │                 │            │             │
# │ video.ai.video │ AI Video       │ Text to Video   │      1,455 │       1,634 │
# │ generator      │ Generator:     │ FLIX            │            │             │
# │                │ Flix AI        │                 │            │             │
# └────────────────┴────────────────┴─────────────────┴────────────┴─────────────┘
#
# Apps Only in AdMob (No Attribution Data):
#                                 AdMob Only (14)
# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┓
# ┃ App Store ID                         ┃ App Name                       ┃ Rows ┃
# ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━┩
# │ 6448867021                           │ AI Chat: Gem Chatbot Assistant │  143 │
# │ 6449147454                           │ Block Puzzle: Brain Test       │    8 │
# │ 6449151063                           │ Triple Match 3D: Matching Game │  132 │
# │ 6469030265                           │ Block Puzzle - Blast 88        │   21 │
# │ aiart.artgenerator.photoenhancer     │ Vista Foto-AI Photo Enhancer   │   40 │
# │ com.bible.holybible.bibleapp         │ Holy Bible - KJV Bible App     │  359 │
# │ com.blockpuzzle.block8x8             │ Block Blast - Puzzle 8x8       │  369 │
# │ com.bloodpressurenow.bpapp           │ Blood Pressure Tracker         │  682 │
# │ com.document.scanner.documentscanner │ QuickDoc Scanner: Snap to docs │  190 │
# │ com.documents.reader.pdf.office      │ Documents Reader DOC, PDF, XLS │  353 │
# │ com.mirror.lightmirror.mirrorapp     │ Mirror App: Mirror Reflector   │  298 │
# │ com.pdf.reader.pdfapp                │ PDF Reader 2023: PDF Viewer    │  205 │
# │ com.tiles.matching.games             │ Tile Match - Matching Games    │    1 │
# │ com.waterreminder.drinkwater.watertr │ Water Tracker : Water Reminder │   63 │
# │ acker                                │                                │      │
# └──────────────────────────────────────┴────────────────────────────────┴──────┘
#
# Apps Only in Adjust (No Revenue Data):
#                              Adjust Only (4)
# ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┓
# ┃ App Name                     ┃ Store ID                         ┃ Rows ┃
# ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━┩
# │ iOS Dont Touch My Phone      │ 6741785920                       │    6 │
# │ Personal AI - Loan EMI       │ ai.personal.finance.assistant    │  164 │
# │ FlixGen                      │ ai.video.template.videogenerator │    4 │
# │ Air Horn Prank: Funny Sounds │ unknown                          │   91 │
# └──────────────────────────────┴──────────────────────────────────┴──────┘
#
# ═══ JOIN ANALYSIS ═══
#
# Date Coverage:
#   AdMob dates:  20251019 to 20251025
#   Adjust dates: 2025-10-19 to 2025-10-25
#
# Sample Join Keys:
#
# AdMob (first 3 rows):
#     date                 app_store_id country_code
# 20251019    com.musicplayer.music.app           AD
# 20251020    com.musicplayer.music.app           AD
# 20251022 com.flashlight.flashlightled           AD
#
# Adjust (first 3 rows):
#        day                          app                           store_id
# country
# 2025-10-22 Haircut Prank Clipper Sounds hairclipper.prank.funnyprank.sound
# India
# 2025-10-23           Text to Video FLIX            video.ai.videogenerator
# India
# 2025-10-25           Text to Video FLIX            video.ai.videogenerator
# India
#
# Country Code Comparison:
#   AdMob:  234 unique (ISO codes)
#   Adjust: 239 unique (ISO codes)
#   ✓ Matched: 233
#   ⚠ AdMob only: 1
#   ⚠ Adjust only: 6
#
# ✓ Matched Country Codes (233):
# AD, AE, AF, AG, AI, AL, AM, AO, AR, AS, AT, AU, AW, AZ, BA, BB, BD, BE, BF, BG,
# BH, BI, BJ, BL, BM, BN, BO, BQ, BR, BS, BT, BW, BY, BZ, CA, CD, CF, CG, CH, CI,
# CK, CL, CM, CN, CO, CR, CU, CV, CW, CY, CZ, DE, DJ, DK, DM, DO, DZ, EC, EE, EG,
# EH, ER, ES, ET, FI, FJ, FK, FM, FO, FR, GA, GB, GD, GE, GF, GG, GH, GI, GL, GM,
# GN, GP, GQ, GR, GT, GU, GW, GY, HK, HN, HR, HT, HU, ID, IE, IL, IM, IN, IO, IQ,
# IR, IS, IT, JE, JM, JO, JP, KE, KG, KH, KI, KM, KN, KR, KW, KY, KZ, LA, LB, LC,
# LI, LK, LR, LS, LT, LU, LV, LY, MA, MD, ME, MF, MG, MH, MK, ML, MM, MN, MO, MP,
# MQ, MR, MS, MT, MU, MV, MW, MX, MY, MZ, NC, NE, NG, NI, NL, NO, NP, NR, NU, NZ,
# OM, PA, PE, PF, PG, PH, PK, PL, PR, PS, PT, PW, PY, QA, RE, RO, RS, RU, RW, SA,
# SB, SC, SD, SE, SG, SH, SI, SJ, SK, SL, SM, SN, SO, SR, SS, ST, SV, SX, SY, SZ,
# TC, TD, TG, TH, TJ, TL, TM, TN, TO, TR, TT, TV, TW, TZ, UA, UG, US, UY, UZ, VC,
# VE, VG, VI, VN, VU, WF, WS, YE, YT, ZA, ZM, ZW, ZZ
#
# ⚠ AdMob Only Country Codes (1):
# XK
#
# ⚠ Adjust Only Country Codes (6):
# AX, MC, NA, NF, PM, TK
# ╭───────────────────── Result ─────────────────────╮
# │ Summary                                          │
# │                                                  │
# │ Total unique apps: 56                            │
# │ ✓ Matched (both sources): 38 (67.9%)             │
# │ ⚠ AdMob only: 14                                 │
# │ ⚠ Adjust only: 4                                 │
# │                                                  │
# │ Next Steps:                                      │
# │ 1. Map app names in dbt intermediate layer       │
# │ 2. Create country code mapping (ISO ↔ Full Name) │
# │ 3. Use LEFT JOIN from AdMob (keep all revenue)   │
# ╰──────────────────────────────────────────────────╯
